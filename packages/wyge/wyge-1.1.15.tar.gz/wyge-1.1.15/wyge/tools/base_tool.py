import json
from typing import TypeVar, Dict, Any, Optional, List, Type, Callable
from dataclasses import dataclass
from functools import wraps

import openai
import openai.pagination
import openai.resources
from pydantic import BaseModel
from openai.resources.chat.completions import ChatCompletion
from wyge.common.logger import logger

# Type definitions
T = TypeVar('T', bound=BaseModel)
ToolFunction = Callable[..., Any]
ToolRegistry = Dict[str, ToolFunction]

@dataclass
class ToolCall:
    """Structured representation of a tool call with results"""
    id: str
    function_name: str
    arguments: Dict[str, Any]
    result: Any = None
    error: Optional[Exception]= None
    
    @property
    def is_successful(self) -> bool:
        return self.error is None
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "function_name": self.function_name,
            "arguments": self.arguments,
            "result": str(self.result) if self.result is not None else None,
            "error": str(self.error) if self.error is not None else None
        }

class BaseTool(BaseModel):
    """Base class for all tools"""
    class Config:
        arbitrary_types_allowed = True

class FunctionRegistry:
    """Registry for tool functions with validation and schema generation"""
    
    _registry: Dict[str, ToolFunction] = {}
    
    @classmethod
    def register(cls, func_name: str, func: ToolFunction) -> None:
        """Register a function in the registry"""
        cls._registry[func_name] = func
        logger.debug(f"Registered function: {func_name}")
    
    @classmethod
    def get(cls, func_name: str) -> ToolFunction:
        """Get a function from the registry"""
        if func_name not in cls._registry:
            raise ValueError(f"Function '{func_name}' not found in registry")
        return cls._registry[func_name]
    
    @classmethod
    def list_functions(cls) -> List[str]:
        """List all registered functions"""
        return list(cls._registry.keys())
    
    @classmethod
    def clear(cls) -> None:
        """Clear the registry"""
        cls._registry.clear()

def tool(model_class: Type[T]):
    """Decorator to register a function as a tool with a Pydantic model schema"""
    
    def decorator(func: ToolFunction):
        # Validate the model has proper documentation
        if not model_class.__doc__:
            raise ValueError(f"Model class '{model_class.__name__}' must have a docstring")
        
        # Enhance the model's schema method to include tool information
        original_schema = model_class.schema
        
        @wraps(original_schema)
        def enhanced_schema(*args, **kwargs):
            schema = original_schema(*args, **kwargs)
            schema['tool_name'] = func.__name__
            schema['description'] = model_class.__doc__ or func.__doc__ or f"Tool for {func.__name__}"
            return schema
        
        # Replace the schema method
        model_class.schema = enhanced_schema
        
        # Register the function
        FunctionRegistry.register(func.__name__, func)
        
        # Return the decorated function
        @wraps(func)
        def wrapper(*args, **kwargs):
            return func(*args, **kwargs)
        
        return wrapper
    
    return decorator

def execute_tool_calls(tool_calls: List[Any], 
                       catch_errors: bool = True) -> List[ToolCall]:
    """Execute a list of tool calls and return their results"""
    results = []
    
    for call in tool_calls:
        try:
            # Parse the tool call
            function_name = call.function.name
            arguments = json.loads(call.function.arguments)
            
            # Get the function from the registry
            func = FunctionRegistry.get(function_name)
            
            # Create a tool call object
            tool_call = ToolCall(
                id=call.id,
                function_name=function_name,
                arguments=arguments
            )
            
            # Execute the function
            try:
                tool_call.result = func(**arguments)
                print("Tool call result:", tool_call.result)
            except Exception as e:
                if catch_errors:
                    tool_call.error = e
                    logger.warning(f"Tool {function_name} failed: {str(e)}")
                else:
                    raise
                    
            results.append(tool_call)
            
        except ValueError as ve:
            logger.error(f"Value error in tool call: {str(ve)}")
            if not catch_errors:
                raise
        except TypeError as te:
            logger.error(f"Type error in tool call: {str(te)}")
            if not catch_errors:
                raise
        except Exception as e:
            logger.error(f"Unexpected error in tool call: {str(e)}")
            if not catch_errors:
                raise
                
    return results

def format_tool_for_api(tool_model: Type[BaseModel]) -> Dict[str, Any]:
    """Format a tool model for the OpenAI API"""
    schema = tool_model.schema()
    function_name = schema.get('tool_name')
    description = schema.get('description')
    properties = schema.get('properties', {})
    required = schema.get('required', [])
    
    parameters = {
        "type": "object",
        "properties": {},
        "required": required
    }
    
    for prop_name, prop_details in properties.items():
        param = {
            "type": prop_details.get('type', 'string'),
            "description": prop_details.get('description', '')
        }
        
        # Handle arrays
        if 'type' in prop_details and prop_details['type'] == 'array':
            param['type'] = 'array'
            param['items'] = {"type": prop_details.get('items', {}).get('type', 'string')}
        
        # Handle enums
        if 'enum' in prop_details:
            param['enum'] = prop_details['enum']
            
        # Handle union types
        if 'anyOf' in prop_details:
            types = [sub_prop['type'] for sub_prop in prop_details['anyOf'] if 'type' in sub_prop]
            param['type'] = types[0] if len(types) == 1 else types
            
        parameters["properties"][prop_name] = param
    
    return {
        "type": "function",
        "function": {
            "name": function_name,
            "description": description,
            "parameters": parameters
        }
    }

class ResponseParser:
    """Parser for OpenAI API responses"""
    
    @staticmethod
    def parse_completion(response: ChatCompletion) -> Dict[str, Any]:
        """Parse a chat completion response into a structured format"""
        choice = response.choices[0]
        message = choice.message
        
        result = {
            'finish_reason': choice.finish_reason,
            'role': message.role,
            'content': message.content,
            'tool_calls': message.tool_calls,
            'function_call': getattr(message, 'function_call', None),
        }
        
        return result
    
    @staticmethod
    def extract_final_answer(content: str) -> Optional[str]:
        """Extract a final answer from assistant's response if it contains the pattern"""
        if not content:
            return None
            
        if 'Final Answer:' in content:
            parts = content.split('Final Answer:', 1)
            if len(parts) > 1:
                return parts[1].strip()
                
        return None