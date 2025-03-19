import os
import json
import time
from typing import Optional, List, Dict, Any, Type, Union

import openai
from pydantic import BaseModel

from wyge.memory.basic_memory import MemoryManager
from wyge.tools.base_tool import ToolCall, execute_tool_calls, format_tool_for_api, ResponseParser
from wyge.common.logger import logger, logging

class ChatOpenAI:
    """Enhanced OpenAI chat model wrapper with advanced features"""
    
    def __init__(
        self,
        api_key: Optional[str] = None,
        model_name: str = 'gpt-4o-mini',  
        temperature: float = 0.2,
        max_tokens: int = 1500,
        tools: Optional[List[Type[BaseModel]]] = None,
        memory_enabled: bool = False,
        memory_size: int = 20,
        default_system_message: str = "You are a helpful assistant.",
        retry_count: int = 3,
        retry_delay: float = 1.0,
        verbose: bool = False
    ):
        # API setup
        self.api_key = api_key or os.getenv('OPENAI_API_KEY')
        if not self.api_key:
            raise ValueError("API key must be provided either via argument or 'OPENAI_API_KEY' environment variable")
        os.environ['OPENAI_API_KEY'] = self.api_key
        
        # Model configuration
        self.model_name = model_name
        self.temperature = temperature
        self.max_tokens = max_tokens
        self._validate_model_config()
        
        # Tools setup
        self.tools = []
        if tools:
            self.register_tools(tools)
        
        # Memory setup
        self.memory_enabled = memory_enabled
        self.memory = MemoryManager() 
        if memory_enabled:
            self.memory = MemoryManager(
                max_size=memory_size,
                default_system_message=default_system_message
            )
        
        # Other settings
        self.retry_count = retry_count
        self.retry_delay = retry_delay
        self.verbose = verbose
        
        # Tracking
        self.usage_stats = {
            'total_tokens': 0,
            'prompt_tokens': 0,
            'completion_tokens': 0,
            'successful_calls': 0,
            'failed_calls': 0,
            'total_cost': 0.0  # Estimated
        }
        
        if verbose:
            logger.setLevel(logging.DEBUG)
        
    def _validate_model_config(self) -> None:
        """Validate model configuration parameters"""
        if not 0 <= self.temperature <= 2:
            raise ValueError("Temperature must be between 0 and 2")
        if self.max_tokens < 1:
            raise ValueError("max_tokens must be positive")
    
    def register_tools(self, tool_models: List[Type[BaseModel]]) -> None:
        """Register tools with the model"""
        for model in tool_models:
            tool_config = format_tool_for_api(model)
            self.tools.append(tool_config)
            logger.debug(f"Registered tool: {tool_config['function']['name']}")
    
    def update_system_message(self, content: str) -> None:
        """Update the system message"""
        self.memory.update_system_message(content)
        if self.memory_enabled:
            self.memory.update_system_message(content)
    
    def _build_messages(self, prompt: Optional[str], system_message: Optional[str]) -> List[Dict[str, Any]]:
        """Build the messages list for the API call"""
        if self.memory_enabled:
            if system_message:
                self.memory.update_system_message(system_message)
            
            if prompt:
                should_summarize = self.memory.add_message('user', prompt)
                if should_summarize:
                    self._summarize_memory()
                    
            return self.memory.get_conversation_history()
        else:
            # Simple message format when memory is disabled
            return [
                {"role": "system", "content": system_message or "You are a helpful assistant."},
                {"role": "user", "content": prompt or ""}
            ]
    
    def _summarize_memory(self) -> None:
        """Summarize the memory using a separate LLM call"""
        if not self.memory_enabled:
            return
            
        def summarizer(messages: List[Dict[str, Any]]) -> str:
            # Convert messages to a string format
            conversation = "\n".join([
                f"{msg['role']}: {msg['content']}" 
                for msg in messages 
                if 'content' in msg and msg['content']
            ])
            
            # Create a summarization prompt
            prompt = (
                "Summarize the following conversation, preserving key information, "
                "numeric data, and the sequence of events. Be concise but thorough:\n\n"
                f"{conversation}"
            )
            
            # Make a new API call just for summarization
            try:
                response = openai.chat.completions.create(
                    model=self.model_name,
                    messages=[
                        {"role": "system", "content": "You are a helpful summarization assistant."},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=0.3,
                    max_tokens=500
                )
                
                if response.choices and response.choices[0].message.content:
                    return response.choices[0].message.content
                return "Failed to generate summary."
            except Exception as e:
                logger.error(f"Summarization failed: {str(e)}")
                return "Conversation summary unavailable due to an error."
        
        self.memory.summarize(summarizer)
    
    def _call_api(self, messages: List[Dict[str, Any]], 
                return_tool_output: bool = False) -> Dict[str, Any]:
        """Make the API call with retry logic"""
        for attempt in range(self.retry_count):
            try:
                if self.verbose:
                    logger.debug(f"API call attempt {attempt+1}/{self.retry_count}")
                    logger.debug(f"Messages: {json.dumps(messages, indent=2)}")
                
                response = openai.chat.completions.create(
                    model=self.model_name,
                    messages=messages,
                    temperature=self.temperature,
                    max_tokens=self.max_tokens,
                    tools=self.tools if self.tools else None
                )
                print("Raw Response: ", response)
                
                # Update usage statistics
                if hasattr(response, 'usage'):
                    self.usage_stats['total_tokens'] += response.usage.total_tokens
                    self.usage_stats['prompt_tokens'] += response.usage.prompt_tokens
                    self.usage_stats['completion_tokens'] += response.usage.completion_tokens
                    # TODO: Add cost estimation based on model pricing
                
                self.usage_stats['successful_calls'] += 1
                
                # Parse the response
                parsed = ResponseParser.parse_completion(response)
                
                if self.verbose:
                    try:
                        logger.debug(f"Response: {json.dumps(parsed, indent=2, cls=ToolCallEncoder)}")
                    except Exception as e:
                        logger.warning(f"Could not serialize response for logging: {str(e)}")
                
                # Check if we need to execute tool calls
                tool_results = None
                
                if parsed['finish_reason'] in ('function_call', 'tool_calls') and parsed['tool_calls']:
                    tool_results = execute_tool_calls(parsed['tool_calls'])
                    
                    if self.verbose:
                        logger.debug(f"Tool results: {json.dumps([t.to_dict() for t in tool_results], indent=2)}")
                    
                    # Add tool results to memory if enabled
                    if self.memory_enabled:
                        # First add the assistant's message with tool calls
                        self.memory.messages.append(response.choices[0].message.to_dict())
                        
                        # Then add each tool result
                        for tool_call in tool_results:
                            self.memory.add_tool_message(tool_call)
                
                return {
                    'response': response,
                    'parsed': parsed,
                    'tool_results': tool_results
                }
                
            except Exception as e:  # Use normal error handling
                self.usage_stats['failed_calls'] += 1
                logger.error(f"API call error (attempt {attempt+1}/{self.retry_count}): {str(e)}")
                
                if attempt < self.retry_count - 1:
                    time.sleep(self.retry_delay * (2 ** attempt))  # Exponential backoff
                else:
                    raise Exception(f"API call failed after {self.retry_count} attempts: {str(e)}")
                
    def run(self, 
            prompt: Optional[str] = None, 
            system_message: Optional[str] = None,
            return_tool_output: bool = False) -> Union[str, List[ToolCall]]:
        """
        Run the model with the given prompt
        
        Args:
            prompt: The user message
            system_message: Optional system message override
            return_tool_output: If True, returns tool results instead of final response
            
        Returns:
            Either the model's response text or tool results depending on return_tool_output
        """
        # Build messages
        messages = self._build_messages(prompt, system_message)
        
        # Make the initial API call
        result = self._call_api(messages, return_tool_output)
        
        # If we need to return tool output directly
        if return_tool_output and result['tool_results']:
            return result['tool_results']
        
        # If we have tool results, make another call to get the final response
        if result['tool_results'] and not self.memory_enabled:
            # Add the assistant's response with tool calls
            messages.append(result['response'].choices[0].message.to_dict())
            
            # Add tool results
            for tool_call in result['tool_results']:
                messages.append({
                    'role': 'tool',
                    'content': json.dumps(tool_call.to_dict()),
                    'tool_call_id': tool_call.id
                })
            
            # Make another API call for the final response
            result = self._call_api(messages)
        
        # Get the final content
        content = result['parsed']['content']
        
        return content
    
    def clear_memory(self, keep_system_message: bool = True) -> None:
        """Clear the conversation memory"""
        if self.memory_enabled:
            self.memory.clear(preserve_system=keep_system_message)
    
    def search_memory(self, query: str, exact_match: bool = False) -> List[Dict[str, Any]]:
        """Search for messages in memory"""
        if self.memory_enabled:
            return self.memory.search(query, exact_match=exact_match)
        return []
    
    def last_message(self) -> Optional[Dict[str, Any]]:
        """Get the last message in memory"""
        if self.memory_enabled and self.memory.messages:
            return self.memory.messages[-1]
        return None
    
    def get_usage_stats(self) -> Dict[str, Any]:
        """Get usage statistics"""
        return self.usage_stats
    
    def get_config(self) -> Dict[str, Any]:
        """Get the current configuration"""
        # Mask API key for security
        masked_api_key = '*' * (len(self.api_key) - 4) + self.api_key[-4:] if self.api_key else None
        
        return {
            'api_key': masked_api_key,
            'model_name': self.model_name,
            'temperature': self.temperature,
            'max_tokens': self.max_tokens,
            'memory_enabled': self.memory_enabled,
            'tools_count': len(self.tools),
            'retry_settings': {
                'count': self.retry_count,
                'delay': self.retry_delay
            },
            'verbose': self.verbose
        }
    
class ToolCallEncoder(json.JSONEncoder):
    def default(self, obj):
        if hasattr(obj, '__dict__'):
            return obj.__dict__
        return str(obj)