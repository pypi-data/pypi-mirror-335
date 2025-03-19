from openai import OpenAI
import base64
from typing import Optional

class VisualQA:
    def __init__(self, api_key: str):
        """Initialize the Visual QA agent with OpenAI API key."""
        self.client = OpenAI(api_key=api_key)
        self.model = "gpt-4o-mini"
        
    def _encode_image(self, image_path: str) -> str:
        """Convert image to base64 string."""
        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode('utf-8')
            
    def ask(self, image_path: str, question: str, max_tokens: int = 300) -> str:
        """
        Ask a question about an image.
        
        Args:
            image_path: Path to the image file
            question: Question about the image
            max_tokens: Maximum tokens for the response
        
        Returns:
            str: AI's response to the question
        """
        base64_image = self._encode_image(image_path)
        
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": question
                        },
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{base64_image}"
                            }
                        }
                    ]
                }
            ],
            max_tokens=max_tokens
        )
        
        return response.choices[0].message.content
