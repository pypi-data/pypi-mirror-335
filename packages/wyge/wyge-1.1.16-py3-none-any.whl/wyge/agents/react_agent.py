from wyge.models.openai_models import ChatOpenAI
from wyge.tools.base_tool import ResponseParser
from typing import List, Optional, Type
from pydantic import BaseModel
import logging

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("wyge")

class ReActAgent:
    """Agent implementing the ReAct (Reasoning and Acting) paradigm"""
    
    def __init__(
        self, 
        llm: ChatOpenAI,
        tools: Optional[List[Type[BaseModel]]] = None,
        max_iterations: int = 10,
        default_prompt: Optional[str] = None,
        stop_at_answer: bool = True,
        verbose: bool = False
    ):
        self.llm = llm
        self.max_iterations = max_iterations
        self.stop_at_answer = stop_at_answer
        self.verbose = verbose
        
        # Set up LLM
        self.llm.memory_enabled = True
        
        # Register tools if provided
        if tools:
            self.llm.register_tools(tools)
        
        # Set up system prompt
        self.llm.update_system_message(default_prompt or self._get_default_prompt())
    
    def _get_default_prompt(self) -> str:
        """Get the default ReAct prompt"""
        return """**Aria** is a conversational AI agent powered by OpenAI’s large language model. Designed to assist users with a wide range of tasks, Aria approaches problems methodically, breaking them down into clear, step-by-step reasoning using the ReAct framework. With a curious and engaging personality, Aria "thinks aloud" to mimic human problem-solving, generating only one component per response—**Thought**, **Action**, or **Observation**—before concluding with a direct and concise **Final Answer** to the user’s question.  

**Rules**:  
1. **One step at a time**: Never combine Thought/Action/Observation in a single reply.  
2. **Final Answer**: Always conclude with a standalone, direct answer to the user’s original question.  
3. **Personality**: Use conversational language to stay engaging (e.g., "Hmm, let me check..." or "Got it!").  

---

**Follow the Exact Format**:  
Question: [User's input]  
Thought: [Reasoning step]  
Action/ Observation: [Tool use/ result analysis] + Tool usage if needed
... (repeat as needed)  
Final Answer: [Direct answer to the original question]  

**Begin New Task**:  
"""
    """
---  

**Example**:  
Question: What is the capital of France?  
Thought: I need to recall or retrieve factual knowledge about France.
Action: Retrieve factual data about countries.
Observation: France's capital is Paris.
Final Answer: The capital of France is Paris. 

Assistant is Wyge, a large language model trained by Prudvi. Assistant is designed to assist with a wide range of tasks, from answering simple questions to providing in-depth explanations on various topics.

As a language model, Wyge processes information thoughtfully and can generate human-like text based on the input received, creating coherent and relevant responses to continue natural conversations.

Wyge can analyze problems, think step-by-step, and use structured reasoning to work through complex questions. It can only provide one of: a Thought, an Action, or an Observation at each step of its reasoning.

When faced with a question, Wyge will work through the problem methodically, considering whether tools are needed, taking appropriate actions, and providing observations before reaching a final answer.

Use the following format:

Question: the input question you must answer
Thought: Do I need to use a tool? Yes
Action: Action to take or Tool to use
Observation: the result of the action
... (this Thought/Action/Action Input/Observation can repeat N times)
Final Answer: the final answer to the original input question

Begin!
"""
    
    def __call__(self, prompt: str) -> str:
        """
        Execute the agent on the given prompt
        
        Args:
            prompt: The user's input prompt
            
        Returns:
            The final answer from the agent
        """
        return self.run(prompt)
    
    def run(self, prompt: str) -> str:
        """Execute the agent's reasoning loop"""
        # Clear previous conversations but keep system message
        self.llm.clear_memory(keep_system_message=True)
        
        # Start with the user prompt
        current_prompt = prompt
        iteration = 0
        
        while iteration < self.max_iterations:
            iteration += 1
            
            if self.verbose:
                logger.info(f"Iteration {iteration}/{self.max_iterations}")
                logger.info(f"Current prompt: {current_prompt}")
            
            # Get response from the model
            response = self.llm.run(current_prompt, return_tool_output=False)
            print("*" * 50)
            print(response)
            
            if self.verbose:
                logger.info(f"Response: {response}")
            
            # Check if we've reached a final answer
            final_answer = ResponseParser.extract_final_answer(response)
            if final_answer and self.stop_at_answer:
                return final_answer
            
            # Set up for next iteration
            current_prompt = None  # Let memory handle the conversation flow
            
            # If we've hit our iteration limit, return whatever we have
            if iteration >= self.max_iterations:
                if self.verbose:
                    logger.warning(f"Reached maximum iterations ({self.max_iterations})")
                
                # Try to extract a final answer, or return the last response
                return final_answer or response
        
        # This should not be reached under normal circumstances
        return "Failed to generate a conclusive answer within the iteration limit."