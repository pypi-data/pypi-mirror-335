import os
from typing import Any
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")

def generate_syllabus(llm: Any, topic: str, task: str) -> str:
    """
    Generate a course syllabus for a given topic using an LLM.
    
    Args:
        llm: The language model to use for generation
        topic: The topic for which to generate a syllabus
        task: The specific task description for syllabus generation
        
    Returns:
        str: The generated syllabus as a string
    """
    # Create a prompt for syllabus generation
    prompt = f"""
    Create a comprehensive course syllabus for teaching {topic}.
    
    The syllabus should include:
    1. Course overview and objectives
    2. A list of 5-10 main topics to cover
    3. For each topic, include 2-3 subtopics or key concepts
    4. Suggested learning resources
    5. A logical progression of topics from basic to advanced
    
    Format the syllabus in a clear, structured way that would be easy for a student to follow.
    {task}
    """
    
    # Generate the syllabus using the provided LLM
    return llm(prompt)