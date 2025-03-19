import pandas as pd
import os
from sqlalchemy import create_engine
from langchain_openai import ChatOpenAI
from langchain_community.utilities.sql_database import SQLDatabase
from langchain_community.agent_toolkits import create_sql_agent

class DataQueryAgent:
    """
    A class that loads data from Excel or CSV files into a SQLite database
    and provides natural language querying capabilities.
    """
    
    def __init__(self, openai_api_key, model_name='gpt-4o-mini', db_path="sql_db"):
        """
        Initialize the DataQueryAgent.
        
        Args:
            model_name (str): The OpenAI model to use for queries
            db_path (str): Path to SQLite database. If None, creates an in-memory database.
        """
        self.model_name = model_name
        self.db_path = db_path if db_path else ':memory:'
        self.engine = create_engine(f'sqlite:///{self.db_path}')
        self.tables = []
        self.llm = ChatOpenAI(model=self.model_name, api_key=openai_api_key)
        self.db = SQLDatabase(engine=self.engine)
        self.agent = None
    
    def load_data(self, file_path, table_name=None, sheet_name=0):
        """
        Load data from Excel or CSV file into the database.
        
        Args:
            file_path (str): Path to the Excel or CSV file
            table_name (str): Name of the table to create. If None, uses filename without extension.
            sheet_name: For Excel files, which sheet to load (default is first sheet)
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Determine file type and read accordingly
            file_ext = os.path.splitext(file_path)[1].lower()
            
            if not table_name:
                table_name = os.path.splitext(os.path.basename(file_path))[0]
            
            # Read the file based on extension
            if file_ext in ['.xlsx', '.xls']:
                df = pd.read_excel(file_path, sheet_name=sheet_name)
            elif file_ext == '.csv':
                df = pd.read_csv(file_path)
            else:
                print(f"Unsupported file type: {file_ext}")
                return False
            
            # Write to database
            df.to_sql(table_name, self.engine, if_exists='replace', index=False)
            
            # Add to list of tables
            if table_name not in self.tables:
                self.tables.append(table_name)
            
            # Refresh the database connection
            self.db = SQLDatabase(engine=self.engine)
            
            # Create the agent
            self.agent = create_sql_agent(
                llm=self.llm,
                db=self.db,
                agent_type="openai-tools",
                verbose=True
            )
            
            print(f"Successfully loaded data into table '{table_name}'")
            return True
            
        except Exception as e:
            print(f"Error loading data: {str(e)}")
            return False
    
    def query(self, question):
        """
        Query the database using natural language.
        
        Args:
            question (str): Natural language question about the data
            
        Returns:
            The response from the agent
        """
        if not self.agent:
            print("No data loaded. Please load data first using load_data().")
            return None
        
        try:
            result = self.agent.invoke(question)
            return result
        except Exception as e:
            print(f"Error during query: {str(e)}")
            return None


if __name__ == "__main__":

    # Initialize the agent
    agent = DataQueryAgent()

    # Load data from a CSV file
    agent.load_data("C:/Users/prudh/Desktop/Latest_Cannatwin_Data.xlsx")

    # Or load data from an Excel file
    # agent.load_data("path/to/your/file.xlsx", sheet_name="Sheet1")

    # Query the data in natural language
    result = agent.query("how many rows are there in the data?")
    print(result)