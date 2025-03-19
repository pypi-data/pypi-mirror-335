from openai import OpenAI
import PyPDF2 as pdf
from docx import Document
import json
from dotenv import load_dotenv
import os
from concurrent.futures import ThreadPoolExecutor
from typing import List, Dict, Any, Tuple, Optional
import io

# Load environment variables
load_dotenv()

class ResumeAnalyzer:
    def __init__(self, api_key):
        self.client = OpenAI(api_key=api_key)
        self.model = "gpt-4o-mini"
        self.max_workers = 5  # Maximum number of concurrent resume analyses  

    def extract_text_from_file(self, file):
        """Extract text from a PDF or DOCX file."""
        try:
            # Get file extension
            file_name = file.name if hasattr(file, 'name') else ''
            file_ext = os.path.splitext(file_name)[1].lower()

            # Handle different file types
            if file_ext == '.pdf':
                return self.extract_text_from_pdf(file)
            elif file_ext == '.docx':
                return self.extract_text_from_docx(file)
            else:
                raise Exception("Unsupported file format. Please upload PDF or DOCX files.")

        except Exception as e:
            raise Exception(f"Error reading file: {e}")

    def extract_text_from_pdf(self, pdf_file):
        """Extract text from a PDF file."""
        try:
            reader = pdf.PdfReader(pdf_file)
            text = ""
            for page in reader.pages:
                text += page.extract_text()
            return text
        except Exception as e:
            raise Exception(f"Error reading PDF file: {e}")

    def extract_text_from_docx(self, docx_file):
        """Extract text from a DOCX file."""
        try:
            # Create a BytesIO object from the file content
            file_bytes = io.BytesIO(docx_file.read())
            # Reset file pointer
            docx_file.seek(0)
            
            doc = Document(file_bytes)
            text = ""
            for paragraph in doc.paragraphs:
                text += paragraph.text + "\n"
            return text
        except Exception as e:
            raise Exception(f"Error reading DOCX file: {e}")

    def analyze_resume(self, resume_text, job_description):
        """Analyze a single resume based on the job description using OpenAI."""
        try:
            prompt = f"""
            You are an ATS system. Analyze this resume and return a JSON object.
            Format your response as a raw JSON object without any additional text or formatting.
            Use exactly this structure:
            {{
                "JD Match": "X%",
                "MissingKeywords": [],
                "Profile Summary": "",
                "Suggestions": []
            }}

            Resume:
            {resume_text}

            Job Description:
            {job_description}
            """

            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are an ATS system. Respond only with valid JSON."},
                    {"role": "user", "content": prompt},
                ],
                temperature=0.5,
                max_tokens=1000,
            )

            content = response.choices[0].message.content.strip()
            
            # Debug logging
            print("Raw API response:", content)
            
            try:
                parsed_json = json.loads(content)
                # Validate required fields
                required_fields = ["JD Match", "MissingKeywords", "Profile Summary", "Suggestions"]
                if all(field in parsed_json for field in required_fields):
                    return parsed_json
                else:
                    raise ValueError("Missing required fields in JSON response")
            except (json.JSONDecodeError, ValueError) as e:
                print(f"JSON parsing error: {str(e)}")
                return {
                    "JD Match": "0%",
                    "MissingKeywords": [],
                    "Profile Summary": "Error: Could not analyze resume",
                    "Suggestions": ["Error processing the resume. Please try again."]
                }
                
        except Exception as e:
            print(f"Analysis error: {str(e)}")
            raise Exception(f"Error analyzing resume: {e}")
            
    def _process_single_resume(self, resume_data: Tuple[str, bytes], job_description: str) -> Dict[str, Any]:
        """Process a single resume for batch processing.
        
        Args:
            resume_data: Tuple containing (filename, file_content)
            job_description: The job description text
            
        Returns:
            Dictionary with analysis results and filename
        """
        filename, file_content = resume_data
        try:
            # Extract text from the resume using the new method
            resume_text = self.extract_text_from_file(file_content)
            
            # Analyze the resume
            result = self.analyze_resume(resume_text, job_description)
            
            # Add filename to the result
            result["filename"] = filename
            return result
        except Exception as e:
            print(f"Error processing resume {filename}: {str(e)}")
            return {
                "filename": filename,
                "JD Match": "0%",
                "MissingKeywords": [],
                "Profile Summary": f"Error: Could not analyze resume - {str(e)}",
                "Suggestions": ["Error processing the resume. Please try again."]
            }
    
    def analyze_multiple_resumes(self, resume_files: List[Tuple[str, bytes]], job_description: str) -> List[Dict[str, Any]]:
        """Analyze multiple resumes based on a single job description.
        
        Args:
            resume_files: List of tuples containing (filename, file_content) for each resume
            job_description: The job description text
            
        Returns:
            List of dictionaries with analysis results for each resume
        """
        results = []
        
        # Use ThreadPoolExecutor for parallel processing
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            # Create a list of future objects
            futures = [executor.submit(self._process_single_resume, resume_file, job_description) 
                      for resume_file in resume_files]
            
            # Collect results as they complete
            for future in futures:
                try:
                    result = future.result()
                    results.append(result)
                except Exception as e:
                    print(f"Error in thread execution: {str(e)}")
        
        # Sort results by JD Match percentage (descending)
        results.sort(key=lambda x: self._parse_percentage(x.get("JD Match", "0%")), reverse=True)
        
        return results
    
    def _parse_percentage(self, percentage_str: str) -> float:
        """Parse percentage string to float for sorting."""
        try:
            return float(percentage_str.strip('%'))
        except (ValueError, AttributeError):
            return 0.0

# Example usage
if __name__ == "__main__":
    analyzer = ResumeAnalyzer()

    # Load job description and resume
    job_description = """
    We are looking for a software engineer with experience in Python, machine learning, and cloud computing.
    The ideal candidate should have strong problem-solving skills, experience with REST APIs, and familiarity with Docker and Kubernetes.
    """

    resume_path = "path/to/resume.pdf"  # Replace with the actual path to your resume

    try:
        # Extract text from the resume
        with open(resume_path, "rb") as pdf_file:
            resume_text = analyzer.extract_text_from_pdf(pdf_file)

        # Analyze the resume
        result = analyzer.analyze_resume(resume_text, job_description)
        print(result)  # Print the result as a dictionary
    except Exception as e:
        print(f"Error: {e}")