"""
Google Gemini LLM integration for SQL generation.
"""
import os
import logging
from typing import List, Dict, Any
import google.generativeai as genai
from google.generativeai.types import GenerationConfig
from smolagents import OpenAIServerModel

class GeminiLLM:
    def __init__(self, model_name: str = "gemini-2.5-flash"):
        # Get API key from environment variable
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("GEMINI_API_KEY environment variable is required")

        # Configure Gemini SDK
        genai.configure(api_key=api_key)
        self.model_name = model_name
        self.model = genai.GenerativeModel(self.model_name)
        self.logger = logging.getLogger(__name__)

    def generate_sql(self, natural_query: str, relevant_tables: List[Dict[str, Any]]) -> str:
        """
        Generate SQL query from natural language query and relevant table information.
        """
        try:
            # Create a prompt with the natural query and relevant table information
            prompt = self._create_prompt(natural_query, relevant_tables)
            # print("RELEVANT_TABLES:",relevant_tables)
            # print("PROMPT",prompt)
            # Generate the SQL query
            response = self.model.generate_content(prompt)

            # Log the response for debugging
            self.logger.debug(f"LLM Response: {response.text}")

            # Extract and return the SQL query
            sql_query = self._extract_sql_query(response.text)

            return sql_query
        except Exception as e:
            self.logger.error(f"Error generating SQL: {str(e)}")
            raise



    def _create_prompt(self, natural_query: str, relevant_tables: List[Dict[str, Any]]) -> str:
        """
        Create a prompt for the LLM with the natural query and relevant table information.
        """
        prompt = f"""
        You are an expert SQL developer. Your task is to convert natural language queries into correct, executable SQL queries.
        
        ## Instructions:
        1. Analyze the provided natural language query carefully.
        2. Use only the table structures provided below.
        3. Generate a valid SQL query that answers the natural language query.
        4. Do not add any explanations or comments, only output the SQL query.
        5. Use proper SQL formatting and best practices.
        6. If multiple tables are relevant, use appropriate JOINs based on primary/foreign key relationships.
        7. Follow standard SQL syntax that works with most databases.
        
        ## Natural Language Query:
        "{natural_query}"
        
        ## Relevant Database Tables and Structures:
        
        """
        # print("TABLES:",relevant_tables)
        for table in relevant_tables:
            prompt += f"\n### Table: `{table['name']}`\n"
            prompt += f"**Columns:**\n"
            for col in table['columns']:
                nullable_str = "NOT NULL" if col.get('nullable', True) == False else "NULL"
                primary_key_str = " (PRIMARY KEY)" if col.get('primary_key', False) else ""
                foreign_key_str = " (FOREIGN KEY)" if col.get('foreign_key', False) else ""
                
                prompt += f"- `{col['name']}`: {col['type']} [{nullable_str}{primary_key_str}{foreign_key_str}]"
                if col.get('default') is not None:
                    prompt += f", default: {col['default']}"
                prompt += "\n"
                
            # Add primary key information
            primary_keys = table.get('primary_keys', [])
            if primary_keys:
                prompt += f"\n**Primary Keys:** {', '.join([f'`{pk}`' for pk in primary_keys])}\n"
            
            # Add foreign key information
            foreign_keys = table.get('foreign_keys', [])
            if foreign_keys:
                prompt += f"\n**Foreign Keys:**\n"
                for fk in foreign_keys:
                    prompt += f"- `{fk['constrained_columns']}` references `{fk['referred_table']}.{fk['referred_columns']}`\n"
        
        prompt += f"""
        
        ## Output:
        Please provide only the SQL query that answers the natural language query. No explanations.
        """
        
        return prompt
    
    def _extract_sql_query(self, response_text: str) -> str:
        """
        Extract the SQL query from the LLM response.
        """
        # Remove common markdown code block indicators and clean up
        cleaned_response = response_text.strip()
        
        # Handle various code block formats
        if "```sql" in cleaned_response:
            start = cleaned_response.find("```sql") + len("```sql")
            end = cleaned_response.find("```", start)
            if end == -1:  # If no closing backticks, use the end of the string
                end = len(cleaned_response)
            sql_query = cleaned_response[start:end].strip()
        elif "```" in cleaned_response:
            start = cleaned_response.find("```")
            # Skip the language identifier if present
            if start + 3 < len(cleaned_response) and cleaned_response[start+3:start+4].isalpha():
                # There's a language identifier like ```python
                next_newline = cleaned_response.find("\n", start)
                start = next_newline if next_newline != -1 else start + 3
            else:
                start += 3  # Skip the ``` part
            end = cleaned_response.find("```", start)
            if end == -1:  # If no closing backticks, use the end of the string
                end = len(cleaned_response)
            sql_query = cleaned_response[start:end].strip()
        else:
            # If no code blocks, return the whole response
            sql_query = cleaned_response
            
        return sql_query
