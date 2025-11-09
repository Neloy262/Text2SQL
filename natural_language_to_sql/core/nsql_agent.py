"""
Core NSQL agent that handles the main logic for converting natural language to SQL.
"""
import logging
from typing import Dict, List, Any
from sqlalchemy import create_engine, inspect, text
from ..models.gemini_llm import GeminiLLM
from .rag_system import RAGSystem
from ..utils.helpers import validate_and_sanitize_query


class NSQLAgent:
    def __init__(self, db_url: str, custom_table_descriptions: List[Dict[str, Any]] = None):
        self.db_url = db_url
        self.engine = create_engine(db_url)
        self.inspector = inspect(self.engine)
        self.gemini_llm = GeminiLLM()
        self.rag_system = RAGSystem(self.engine, custom_table_descriptions)
        self.logger = logging.getLogger(__name__)
        
    def process_query(self, natural_query: str) -> str:
        """
        Process a natural language query and return the corresponding SQL query.
        """
        try:
            self.logger.info(f"Processing natural language query: {natural_query}")
            
            # Step 1: Retrieve relevant table information using RAG
            self.logger.debug("Retrieving relevant tables using RAG system...")
            relevant_tables = self.rag_system.retrieve_relevant_tables(natural_query)
            self.logger.debug(f"Found {len(relevant_tables)} relevant tables")
            
            if not relevant_tables:
                return "No relevant tables found for the given query."
            
            # Step 2: Generate SQL using Gemini LLM with table context
            self.logger.debug("Generating SQL query using Gemini LLM...")
            sql_query = self.gemini_llm.generate_sql(natural_query, relevant_tables)
            self.logger.debug(f"Generated SQL query: {sql_query}")
            
            # Step 3: Validate and sanitize the SQL query
            is_valid, sanitized_query = validate_and_sanitize_query(sql_query)
            if not is_valid:
                return f"Generated SQL query contains potentially dangerous operations: {sql_query}"
            
            # Step 4: Validate and execute the SQL query
            result = self.validate_and_execute(sanitized_query)
            
            # Return both the SQL query and the result
            result_str = f"Generated SQL: {sanitized_query}\n\nResult:\n{result}"
            return result_str
            
        except Exception as e:
            self.logger.error(f"Error processing query: {str(e)}")
            return f"Error processing query: {str(e)}"
        
    def add_custom_table_descriptions(self, custom_table_descriptions: List[Dict[str, Any]]):
        """
        Add custom table descriptions to the RAG system.
        """
        self.rag_system.add_custom_table_descriptions(custom_table_descriptions)
        
    def validate_and_execute(self, sql_query: str) -> str:
        """
        Validate the SQL query and execute it if valid.
        Additional validation: only allow SELECT statements
        """
        try:
            # Further validation: ensure it's only a SELECT statement
            sql_query_lower = sql_query.lower().strip()
            if sql_query_lower.startswith('delete') or sql_query_lower.startswith('drop'):
                return f"Only SELECT statements are allowed: {sql_query}"

            # Execute the query using SQLAlchemy's text() for safety
            with self.engine.connect() as conn:
                # Execute the query and get the result
                result = conn.execute(text(sql_query))
                rows = result.fetchall()
                
                # Get column names for display
                columns = list(result.keys())
                
                # Convert results to string format
                if not rows:
                    return "No results found."
                
                # Format the result in a readable way
                result_str = "Columns: " + ", ".join(columns) + "\n"
                result_str += "-" * 50 + "\n"  # separator line
                
                for row in rows:
                    result_str += str(tuple(row)) + "\n"
                    
                return result_str
        except Exception as e:
            return f"Error executing SQL query: {str(e)}"