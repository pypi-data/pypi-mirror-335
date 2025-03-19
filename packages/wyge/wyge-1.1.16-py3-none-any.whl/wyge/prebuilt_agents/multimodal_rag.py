import base64
from io import BytesIO
import json
import pandas as pd
from PIL import Image
import chromadb
import openai
from langchain.text_splitter import RecursiveCharacterTextSplitter
import IPython.display
from typing import List, Dict, Any, Tuple, Optional
import os
from wyge.prebuilt_agents.pdf_extractor import PDFExtractor

class MultiModalRAG:
    def __init__(self, openai_api_key: str, vector_db_path: str = "./vector_db2"):
        self.openai_client = openai.OpenAI(api_key=openai_api_key)
        self.chroma_client = chromadb.PersistentClient(path=vector_db_path)
        try:
            # self.chroma_client.get_collection("pdf_data48734")
            self.chroma_client.delete_collection("pdf_data")
        except ValueError:
            pass  # Collection does not exist, no need to delete
        # self.collection = self.chroma_client.get_or_create_collection("pdf_data1")
        self.collection = self.chroma_client.create_collection("pdf_data")

    def clear_collection(self):
        """Clear all documents from the collection"""
        try:
            self.chroma_client.delete_collection("pdf_data")
        except Exception:
            print("Failed to delete collection. Recreating collection...")

    def extract_pdf_content(self, pdf_path: str, page_range: Tuple[int, int] = (1, 10)) -> Tuple[List, List, List]:
        extractor = PDFExtractor(pdf_path, page_range=page_range)
        return extractor.extract_text(), extractor.extract_tables(table_flavor='lattice'), extractor.extract_images()

    def split_text(self, texts: List[str], chunk_size: int = 2048, chunk_overlap: int = 50) -> List[str]:
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=chunk_size, chunk_overlap=chunk_overlap)
        return text_splitter.split_text(" ".join(texts))

    def process_tables(self, tables: List[Dict]) -> List[Dict]:
        table_chunks = []
        for table in tables:
            if not table["content"]:
                continue
            rows = table["content"]
            header_keys = list(rows[0].keys())
            formatted_table = "\n".join([
                ", ".join([f"{key}: {row[key]}" for key in header_keys])
                for row in rows
            ])
            table_chunks.append({
                "content": formatted_table,
                "metadata": table["metadata"]
            })
        return table_chunks

    def get_embedding(self, text: str) -> List[float]:
        if not isinstance(text, str):
            text = json.dumps(text)
        response = self.openai_client.embeddings.create(input=text, model="text-embedding-ada-002")
        return response.data[0].embedding

    def store_in_vector_db(self, chunks: List[Dict], prefix: str = "chunk"):
        for i, chunk in enumerate(chunks):
            embedding = self.get_embedding(chunk["content"])
            self.collection.add(
                documents=[chunk["content"]],
                embeddings=[embedding],
                ids=[f"{prefix}_{i}"],
                metadatas=chunk["metadata"]
            )

    def generate_summary(self, data: bytes, type: str) -> Tuple[str, Optional[str]]:
        if type == 'image':
            image_base64 = base64.b64encode(data).decode("utf-8")
            response = self.openai_client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "Describe this image in detail."},
                    {"role": "user", "content": [{"type": "image_url", "image_url": {"url": f"data:image/png;base64,{image_base64}"}}]}
                ]
            )
            print(response.choices[0].message.content)
            return response.choices[0].message.content, image_base64
        elif type == 'table':
            print(data)
            response = self.openai_client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "Structure this table in a readable format. Include column names and data. Also provide a summary of the table."},
                    {"role": "user", "content": data}
                ]
            )
            print(response.choices[0].message.content)
            return response.choices[0].message.content, None

    def process_pdf(self, pdf_path: str, page_range: Tuple[int, int]):
        # Clear existing data before processing new PDF
        # self.clear_collection()
        
        texts, tables, images = self.extract_pdf_content(pdf_path, page_range)
        # print(texts, tables, images)
        
        # Process text
        text_chunks = self.split_text([t['content'] for t in texts])
        print(0.5)
        print(text_chunks)
        self.store_in_vector_db([{'content': chunk, 'metadata': None} for chunk in text_chunks], prefix="text")
        print(1)
        # Process tables
        table_chunks = self.process_tables(tables)
        # table_chunks_summaries = self.generate_summary(table_chunks, type='table')
        final_table_chunks = []
        for i, table_chunk in enumerate(table_chunks):
            final_table_chunks.append({
                "content": self.generate_summary(table_chunk['content'], type='table')[0],
                "metadata": {"raw table" : table_chunk['content']}
            })
            # final_table_chunks[i]["content"], _ = self.generate_summary(table_chunk["content"], type='table')
            # final_table_chunks[i]["metadata"] = table_chunk
        print(1.5)
        print(final_table_chunks)
        print(1.75)
        print(final_table_chunks[0])
        self.store_in_vector_db(final_table_chunks, prefix="table")
        print(2)
        # Process images
        for i, img in enumerate(images):
            image_summary, image_base64 = self.generate_summary(img['content'], type='image')
            embedding = self.get_embedding(image_summary)
            self.collection.add(
                documents=[image_base64],
                embeddings=[embedding],
                ids=[f"image_{i}"],
                metadatas=[{"summary": image_summary}]
            )
        print(3)

    def display_result(self, result: Dict[str, Any]):
        """Display different types of content appropriately"""
        for i, (doc_id, content, metadata) in enumerate(zip(result["ids"], result["content"], result["metadata"]), 1):
            if doc_id.startswith("image_"):
                # Display image
                image_data = base64.b64decode(content)
                IPython.display.display(Image.open(BytesIO(image_data)))
                print(f"Image Summary: {metadata.get('summary', 'No summary available')}\n")
                
            elif doc_id.startswith("table_"):
                # Display table in a formatted way
                print("Table Content:")
                try:
                    # Split rows and create DataFrame
                    rows = [row.strip().split(',') for row in content.split('\n')]
                    df = pd.DataFrame(rows)
                    IPython.display.display(df)
                except:
                    print(content)
                print()
                
            else:
                # Display text
                print("Text Content:")
                print(content)
                print()

    def query(self, query_text: str, top_k: int = 5) -> Dict:
        query_embedding = self.get_embedding(query_text)
        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=top_k
        )
        
        return {
            "ids": results['ids'][0],
            "content": results['documents'][0],
            "metadata": results['metadatas'][0]
        }

    def answer_user_query(self, query: str, top_k: int = 5) -> Tuple[str, Dict]:
        """Retrieves relevant data and generates a response using OpenAI LLM."""
        # Step 1: Retrieve data from vector DB
        retrieved_data = self.query(query, top_k=top_k)
        
        # Step 2: Separate images from text + tables
        text_tables = []
        images = []
        
        for doc_id, content in zip(retrieved_data["ids"], retrieved_data["content"]):
            if doc_id.startswith("image_"):
                images.append(content)
            else:
                text_tables.append(content)
        
        # Step 3: Construct messages for LLM
        messages = [{"role": "system", "content": "You are an expert assistant providing precise answers based on retrieved context and image(if available)."}]
        
        if text_tables:
            context_text = "\n\n".join(text_tables)
            messages.append({"role": "user", "content": f"Context:\n{context_text}"})
        
        # Step 4: Add images if they exist
        if images:
            for img_base64 in images:
                messages.append({
                    "role": "user", 
                    "content": [{
                        "type": "image_url",
                        "image_url": {"url": f"data:image/png;base64,{img_base64}"}
                    }]
                })

        if text_tables:
            query = f"Answer the following question based on the context provided by user.\n{query}"
            messages.append({"role": "user", "content": query})
        if images:
            query = f"Answer the following question based on the context and also image provided by user.\n{query}"
            messages.append({"role": "user", "content": query})
        
        # Step 5: Query OpenAI LLM
        response = self.openai_client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages,
            max_tokens=1000
        )
        
        llm_response = response.choices[0].message.content
        print("\nAssistant Response:\n", llm_response)

        # Display images if in IPython environment
        if images and 'IPython' in globals():
            for img_base64 in images:
                image_data = base64.b64decode(img_base64)
                IPython.display.display(Image.open(BytesIO(image_data)))

        return llm_response, retrieved_data

# Example usage:
if __name__ == "__main__":
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    rag = MultiModalRAG(OPENAI_API_KEY)
    
    # # Process a PDF
    rag.process_pdf("C:/Users/prudh/Downloads/integrated-report-consolidated.pdf", page_range=(150, 155))
    
    result = rag.query("scope 1 emmission", top_k=3)
    print(result)
    rag.display_result(result)

    # Query with the new method
    # response = rag.answer_user_query("What is the highest KMP compensation?", top_k=3)
    # print(response)