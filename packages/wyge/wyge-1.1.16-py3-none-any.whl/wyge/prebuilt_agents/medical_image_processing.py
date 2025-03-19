import base64
import os
from dotenv import load_dotenv
from openai import OpenAI
import tempfile

load_dotenv()

class MedicalImageAnalyzer:
    def __init__(self, api_key):
        self.client = OpenAI(api_key=api_key)
        self.sample_prompt = """You are a medical practitioner and an expert in analyzing medical-related images working for a very reputed hospital. You will be provided with images and you need to identify the anomalies, any disease or health issues. You need to generate the result in a detailed manner. Write all the findings, next steps, recommendations, etc. You only need to respond if the image is related to a human body and health issues. You must have to answer but also write a disclaimer saying that "Consult with a Doctor before making any decisions".

Remember, if certain aspects are not clear from the image, it's okay to state 'Unable to determine based on the provided image.'

Now analyze the image and answer the above questions in the same structured manner defined above."""

    def encode_image(self, image_path):
        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode('utf-8')

    def call_gpt4_model_for_analysis(self, filename):
        base64_image = self.encode_image(filename)
        
        messages = [
            {
                "role": "user",
                "content":[
                    {
                        "type": "text", "text": self.sample_prompt
                    },
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/jpeg;base64,{base64_image}",
                            "detail": "high"
                        }
                    }
                ]
            }
        ]

        response = self.client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages,
            max_tokens=1500
        )

        return response.choices[0].message.content

    def chat_eli(self, query):
        eli5_prompt = "You have to explain the below piece of information to a five-year-old. \n" + query
        messages = [
            {
                "role": "user",
                "content": eli5_prompt
            }
        ]

        response = self.client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=messages,
            max_tokens=1500
        )

        return response.choices[0].message.content

    def analyze_image(self, image_path):
        result = self.call_gpt4_model_for_analysis(image_path)
        return result

    def simplify_explanation(self, result):
        simplified_explanation = self.chat_eli(result)
        return simplified_explanation

# Example usage:
if __name__ == "__main__":
    analyzer = MedicalImageAnalyzer()
    
    # Example image path
    image_path = "path_to_your_image.jpg"
    
    # Analyze the image
    result = analyzer.analyze_image(image_path)
    print("Analysis Result:")
    print(result)
    
    # Get simplified explanation
    simplified_explanation = analyzer.simplify_explanation(result)
    print("\nSimplified Explanation:")
    print(simplified_explanation)