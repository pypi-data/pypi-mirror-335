from langchain_openai import ChatOpenAI
from langchain.agents import AgentExecutor, create_openai_tools_agent
from langchain import hub
from langchain.tools import StructuredTool

def extract_audio_from_video(video_file_path, output_audio_path):
    import subprocess
    try:
        # Use ffmpeg to extract audio from video
        command = [
            'ffmpeg',
            '-i', video_file_path,  # Input video file
            '-vn',  # Disable video recording
            '-acodec', 'libmp3lame',  # Use MP3 audio codec
            '-q:a', '2',  # Audio quality (2 is high quality)
            output_audio_path  # Output audio file
        ]
        subprocess.run(command, check=True, capture_output=True)
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error extracting audio: {e.stderr}")
        raise
    except Exception as e:
        print(f"Unexpected error: {str(e)}")
        raise

class ResearchAgent:
    def __init__(self, api_key=None) -> None:
        self.api_key = api_key

        web_tool = StructuredTool.from_function(
            name="website_research",
            func=extract_relevant_sections_from_website,
            description=("Extract relevant information from a website based on keywords. "
            "Args: url (str): The URL of the website to analyze., "
            "keywords (list): A comprehesive list of keywords to search in the website based on the topic(more than 10). "
            "Returns: dict: A dictionary of relevant sections from the website."
            )
        )
        yt_tool = StructuredTool.from_function(
            name="youtube_transcript",  
            func=youtube_transcript_loader,
            description="Extract transcript from a YouTube video"
        )

        self.llm = ChatOpenAI(model="gpt-4o-mini", api_key=api_key).bind_tools([web_tool, yt_tool])

    def extract_video_transcript(self, video_path):
        try:
            # Generate a temporary audio file path
            temp_audio_path = video_path + ".mp3"
            
            # Extract audio from video
            extract_audio_from_video(video_path, temp_audio_path)
            
            # Transcribe the extracted audio
            transcript = self.extract_audio_transcript(temp_audio_path)
            
            # Clean up temporary audio file
            import os
            if os.path.exists(temp_audio_path):
                os.remove(temp_audio_path)
                
            return transcript
        except Exception as e:
            raise Exception(f"Error processing video: {str(e)}")

    def research_website(self, topic, url): 
        prompt1 = (
            f"Gather relavent information about topic from the website. "
            f"\nTopic: {topic} "
            f"\nWebsite: {url} "
        )

        res = self.llm.invoke(prompt1)

        return extract_relevant_sections_from_website(**res.tool_calls[0]['args'])
    
    def extract_transcript_from_yt_video(self, url):
        prompt1 = f"Extract the text content from the youtube video. video url: {url}"

        res = self.llm.invoke(prompt1)
        print(res)
        return youtube_transcript_loader(**res.tool_calls[0]['args'])

    def extract_audio_transcript(self, audio_path):
        return transcribe_audio(audio_path, self.api_key)

class BlogAgent:
    def __init__(self, api_key=None) -> None:
        self.llm = ChatOpenAI(model="gpt-4o-mini", api_key=api_key)

    def write_blog_text(self, topic, context):
        prompt2 = (
            f"You are an effective Blog writer. Output only blog, without any additional text. "
            f"Write a comprehensive blog post based on the following details:\n\n"
            f"Topic: {topic}\n"
            f"Summarized context about the topic: {context}\n\n"
            f"The blog should include an engaging introduction to topic, then detailed stections about how the context addresses the topic, "
            f"and a conclusion summarizing the key points. Structure the blog with clear headings, and write it in a conversational style.  "
            f"Output the blog in markdown format, including a title, introduction, body sections, and conclusion. Write in a conversational style to engage readers. "
        )

        blog_text = self.llm.invoke(prompt2)
        return blog_text.content

    def generate_blog(self, topic, content):
        self.topic = topic
        blog_text = self.write_blog_text(topic, content)

        return blog_text

class LinkedInAgent:
    def __init__(self, api_key=None) -> None:
        self.llm = ChatOpenAI(api_key=api_key)

    def generate_linkedin_post(self, topic, content):
        prompt1 = (
            "Create a LinkedIn post based on the following topic and blog. The post should be professional, engaging, and suitable for a LinkedIn audience. "
            "It should introduce the topic, provide a brief summary, and include a call-to-action if relevant. The text should be concise yet informative."
            f"Topic: {topic}\n"
            f"Summarized context about the topic: {content}\n\n"
            "Expected Output: A well-structured LinkedIn post(around 250 words)."
            "Note: Do not post it on LinkedIn."
        )
        content = self.llm.invoke(prompt1)
        return content.content
    

def extract_sections(url):
    import requests
    from bs4 import BeautifulSoup

    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')
    
    sections = []
    for link in soup.find_all('a', href=True):
        sections.append({
            'text': link.get_text().strip(),
            'url': link['href']
        })
        
    return sections

def filter_relevant_sections(sections, keywords):
    relevant_sections = []
    for section in sections:
        if any(keyword.lower() in section['text'].lower() for keyword in keywords):
            relevant_sections.append(section)
    
    return relevant_sections

def filter_youtube_links(sections):
    youtube_sections = []
    for section in sections.copy():  # Use copy to avoid modifying during iteration
        if 'youtube' in section['url']:
            youtube_sections.append(section)
    return youtube_sections

def gather_info_from_sections(relevant_sections):
    import requests
    from bs4 import BeautifulSoup

    content = {}
    for section in relevant_sections:
        try:
            response = requests.get(section['url'])
            soup = BeautifulSoup(response.content, 'html.parser')
            clean_text = clean_scraped_text(soup.get_text())
            content[section['url']] = clean_text
        except Exception as e:
            # print(e)
            pass
    
    return content

def clean_scraped_text(text):
    import re

    text = re.sub(r'\n+', '\n', text)
    text = re.sub(r'\s+', ' ', text)

    patterns = [
        r'Home\s+About Us.*?\s+Contact Us',
        r'This website uses cookies.*?Privacy & Cookies Policy',  
        r'Copyright.*?Powered by.*',  
    ]

    for pattern in patterns:
        text = re.sub(pattern, '', text, flags=re.DOTALL | re.IGNORECASE)

    text = re.sub(r'\|.*?\|', '', text)  
    text = text.strip()  

    return text

def youtube_transcript_loader(url):
    from youtube_transcript_api import YouTubeTranscriptApi
    try:
        video_id = url.split('/')[-1].split('=')[-1]
        transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)
        transcript = transcript_list.find_transcript(['en'])

        if transcript is None:
            raise ValueError('No English transcript found for video: {}'.format(video_id))

        list_t =  transcript.fetch()
    
        transcript_text = ""
        for transcript in list_t:
            transcript_text += transcript['text'] + " "
        return transcript_text
    except Exception as e:
        # return f"Error: {e}"
        raise 
    
def gather_youtube_data(sections, keywords):

    youtube_sections = []
    for i, section in enumerate(sections):
        if 'youtube' in section['url']:
            youtube_sections.append(section)

    content = {}
    for section in youtube_sections:
        text = youtube_transcript_loader(section['url'])
        if text is not None:
            content[section['url']] = text

    relevant_content = {}
    for k, v in content.items():
        if any(keyword.lower() in v.lower() for keyword in keywords):
            relevant_content[k] = v

    return relevant_content

def extract_relevant_sections_from_website(url, keywords):
    try:
        sections = extract_sections(url)
        filtered_sections = filter_relevant_sections(sections, keywords)
        gathered_info = gather_info_from_sections(filtered_sections)
        youtube_info = gather_youtube_data(sections, keywords)
        total_info = gathered_info | youtube_info
        refined_info = {url: text for url, text in total_info.items() if len(text) > 200}  # Example threshold for content length
        return refined_info
    except Exception as e:
        # return {"error": str(e)}
        raise

def transcribe_audio(audio_file_path, api_key):
    from openai import OpenAI
    client = OpenAI(api_key=api_key)
    with open(audio_file_path, "rb") as audio_file:
        transcription = client.audio.transcriptions.create(
            model="whisper-1",
            file=audio_file
        )   
    return transcription.text

def convert_md_to_docx(md_file_path, docx_file_path):
    import pypandoc

    output = pypandoc.convert_file(md_file_path, 'docx', outputfile=docx_file_path)
    assert output == "", "Conversion failed"