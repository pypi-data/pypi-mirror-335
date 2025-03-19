import os
from typing import Dict, List, Any
from dotenv import load_dotenv
from langchain import PromptTemplate

# Load environment variables
load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")

# Define the instructor prompt template
INSTRUCTOR_PROMPT = """
As a teaching assistant, your task is to teach the user based on the provided syllabus.
The syllabus outlines the specific topics, concepts, and learning objectives to be covered.

Syllabus for {topic}:
{syllabus}

Follow the topics in order and provide comprehensive instruction to convey the knowledge to the user.
Maintain a supportive and approachable demeanor, creating a positive learning environment.

Previous conversation:
{conversation_history}

Provide a clear, concise response to continue the lesson.
"""

def create_teaching_agent(llm: Any) -> Dict:
    """
    Create a teaching agent that can provide educational responses based on a syllabus.
    
    Args:
        llm: The language model to use for generating responses
        
    Returns:
        Dict: A dictionary containing the teaching agent state and functions
    """
    # Initialize the agent state
    agent_state = {
        "syllabus": "",
        "topic": "",
        "conversation_history": []
    }
    
    # Create a function to seed the agent with a syllabus and topic
    def seed(syllabus: str, topic: str) -> None:
        agent_state["syllabus"] = syllabus
        agent_state["topic"] = topic
        agent_state["conversation_history"] = []
    
    # Create a function to add a user message to the conversation history
    def add_user_message(message: str) -> None:
        agent_state["conversation_history"].append(f"User: {message}")
    
    # Create a function to generate a response from the agent
    def generate_response() -> str:
        # Create the prompt template
        prompt_template = PromptTemplate(
            template=INSTRUCTOR_PROMPT,
            input_variables=["syllabus", "topic", "conversation_history"]
        )
        
        # Format the prompt with the current state
        prompt = prompt_template.format(
            syllabus=agent_state["syllabus"],
            topic=agent_state["topic"],
            conversation_history="\n".join(agent_state["conversation_history"])
        )
        
        # Generate the response using the provided LLM
        response = llm(prompt)
        
        # Add the response to the conversation history
        agent_state["conversation_history"].append(f"Assistant: {response}")
        
        return response
    
    # Return the agent interface
    return {
        "seed": seed,
        "add_user_message": add_user_message,
        "generate_response": generate_response
    }

def teaching_agent_fun(llm: Any) -> Dict:
    """
    Factory function to create a teaching agent.
    
    Args:
        llm: The language model to use for generating responses
        
    Returns:
        Dict: A dictionary containing the teaching agent functions
    """
    return create_teaching_agent(llm)