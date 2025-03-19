from langchain_community.document_loaders import TextLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.embeddings import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS
from langchain.prompts import ChatPromptTemplate
from langchain_community.chat_models import ChatOpenAI
from langchain.schema.runnable import RunnablePassthrough
from langchain.schema.output_parser import StrOutputParser
from langchain.schema import Document
from PyPDF2 import PdfReader

class CustomPDFLoader:
    def __init__(self, file_path, page_range=None):
        self.file_path = file_path
        self.page_range = page_range

    def load(self):
        reader = PdfReader(self.file_path)
        text = ""
        
        if self.page_range:
            start_page, end_page = self.page_range
            for i, page in enumerate(reader.pages):
                if i >= start_page and i <= end_page:
                    text += page.extract_text() + "\n"
        else:
            for page in reader.pages:
                text += page.extract_text() + "\n"
        
        return [Document(page_content=text, metadata={"source": self.file_path, "page_range": self.page_range})]


class RAGApplication:
    def __init__(self, file_paths, openai_api_key, model_name="gpt-4o-mini", chunk_size=500, chunk_overlap=50, page_range=None, index="faiss_index"):
        self.page_range = page_range
        self.file_paths = file_paths
        self.openai_api_key = openai_api_key
        self.model_name = model_name
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.embeddings = OpenAIEmbeddings(api_key=self.openai_api_key)
        self.vectorstore = None
        self.retriever = None
        self.rag_chain = None
        self.index = index
        self._initialize_components()

    def _initialize_components(self):
        text_chunks = []

        # Load and split each document
        for file_path in self.file_paths:
            if file_path.endswith('.pdf'):
                loader = CustomPDFLoader(file_path, self.page_range)
            else:
                loader = TextLoader(file_path, encoding="utf8")

            document = loader.load()
            text_splitter = RecursiveCharacterTextSplitter(chunk_size=self.chunk_size, chunk_overlap=self.chunk_overlap)
            chunks = text_splitter.split_documents(document)
            text_chunks.extend(chunks)

        # Create vector store and retriever
        self.vectorstore = FAISS.from_documents(text_chunks, self.embeddings)
        self.vectorstore.save_local(self.index)
        self.retriever = self.vectorstore.as_retriever()

        # Set up the RAG chain
        template = """You are an assistant for question-answering tasks.
        Use the following pieces of retrieved context to answer the question.
        If you don't know the answer, just say that you don't know.
        Keep your answer straight to the point and concise.
        Do not add any additional information.

        Question: {question}
        Context: {context}
        
        Answer:
        """
        prompt = ChatPromptTemplate.from_template(template)
        llm_model = ChatOpenAI(openai_api_key=self.openai_api_key, model_name=self.model_name)
        output_parser = StrOutputParser()

        self.rag_chain = (
            {"context": self.retriever, "question": RunnablePassthrough()}
            | prompt
            | llm_model
            | output_parser
        )

    def query(self, question):
        return self.rag_chain.invoke(question)

# Example usage:
if __name__ == "__main__":
    rag_app = RAGApplication(file_paths=["C:/Users/prudh/Desktop/Resume.pdf"], openai_api_key="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")
    print(rag_app.query("what is my name?"))
    print(rag_app.query("What are my skills?"))
