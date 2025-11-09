"""
RAG (Retrieval Augmented Generation) system for retrieving relevant table information.
"""
from typing import List, Dict, Any
from sqlalchemy import inspect
from typing import List, Dict, Any
from sqlalchemy import inspect
from sentence_transformers import SentenceTransformer
import faiss
import numpy as np
import pandas as pd
import faiss
import numpy as np
import pandas as pd


class RAGSystem:
    def __init__(self, engine, custom_table_descriptions=None):
        self.engine = engine
        self.inspector = inspect(engine)
        # self.model = SentenceTransformer('all-MiniLM-L6-v2')  # Lightweight model for embeddings
        self.model = SentenceTransformer('sentence-transformers/all-mpnet-base-v2')  # Lightweight model for embeddings

        # Build the table index
        self.table_descriptions = self._get_table_descriptions(custom_table_descriptions)
        self._build_index()
        
    def _get_table_descriptions(self, custom_table_descriptions=None) -> List[Dict[str, Any]]:
        """Extract descriptions for all tables in the database."""
        descriptions = []
        
        # Add descriptions for tables in the database
        for table_name in self.inspector.get_table_names():
            # Get columns info
            columns_info = self.inspector.get_columns(table_name)
            
            # Get primary keys
            primary_keys = [col['name'] for col in columns_info if col.get('primary_key', False)]
            
            # Get foreign keys
            foreign_keys = self.inspector.get_foreign_keys(table_name)
            
            # Create table description
            table_description = {
                'name': table_name,
                'columns': [],
                'primary_keys': primary_keys,
                'foreign_keys': foreign_keys,
                'is_custom': False  # Mark as not custom
            }
            
            for col in columns_info:
                col_info = {
                    'name': col['name'],
                    'type': str(col['type']),
                    'nullable': col.get('nullable', True),
                    'default': col.get('default', None),
                    'primary_key': col.get('primary_key', False),
                    'foreign_key': any(fk['constrained_columns'] and col['name'] in fk['constrained_columns'] for fk in foreign_keys)
                }
                table_description['columns'].append(col_info)
                
            # Create a comprehensive text description of the table for embeddings
            text_description = f"Table '{table_name}' has "
            
            # Add column information
            if columns_info:
                text_description += f"{len(columns_info)} columns: "
                for i, col in enumerate(columns_info):
                    text_description += f"{col['name']} of type {col['type']}"
                    if col.get('primary_key'):
                        text_description += " (primary key)"
                    if col.get('nullable', True) == False:
                        text_description += " (not null)"
                    if i < len(columns_info) - 1:
                        text_description += ", "
            
            # Add foreign key information
            if foreign_keys:
                text_description += f". It has foreign keys: "
                for i, fk in enumerate(foreign_keys):
                    text_description += f"'{fk['constrained_columns']}' references '{fk['referred_table']}.{fk['referred_columns']}'"
                    if i < len(foreign_keys) - 1:
                        text_description += ", "
            
            # Add primary key information
            if primary_keys:
                text_description += f". Primary keys: {', '.join(primary_keys)}."
            
            table_description['text_description'] = text_description
            descriptions.append(table_description)
        
        # Add custom table descriptions if provided
        if custom_table_descriptions:
            for custom_table in custom_table_descriptions:
                table_description = {
                    'name': custom_table['name'],
                    'columns': custom_table.get('columns', []),
                    'primary_keys': custom_table.get('primary_keys', []),
                    'foreign_keys': custom_table.get('foreign_keys', []),
                    'is_custom': True  # Mark as custom
                }
                
                # Create a text description for the custom table
                text_description = f"Table '{custom_table['name']}' has "
                
                if table_description['columns']:
                    text_description += f"{len(table_description['columns'])} columns: "
                    for i, col in enumerate(table_description['columns']):
                        text_description += f"{col['name']} of type {col['type']}"
                        if col.get('primary_key'):
                            text_description += " (primary key)"
                        if col.get('nullable', True) == False:
                            text_description += " (not null)"
                        if i < len(table_description['columns']) - 1:
                            text_description += ", "
                
                # Add primary key information
                if table_description['primary_keys']:
                    text_description += f". Primary keys: {', '.join(table_description['primary_keys'])}."
                
                # Add foreign key information
                if table_description['foreign_keys']:
                    text_description += f". It has foreign keys: "
                    for i, fk in enumerate(table_description['foreign_keys']):
                        text_description += f"'{fk['constrained_columns']}' references '{fk['referred_table']}.{fk['referred_columns']}'"
                        if i < len(table_description['foreign_keys']) - 1:
                            text_description += ", "
                
                table_description['text_description'] = text_description
                descriptions.append(table_description)
            
        return descriptions
    
    def _build_index(self):
        """Build FAISS index for similarity search."""
        # Get embeddings for all table descriptions
        descriptions = [table['text_description'] for table in self.table_descriptions]
        embeddings = self.model.encode(descriptions)
        
        # Normalize embeddings for cosine similarity
        embeddings = embeddings.astype('float32')
        faiss.normalize_L2(embeddings)
        
        # Create FAISS index
        dimension = embeddings.shape[1]
        self.index = faiss.IndexFlatIP(dimension)  # Inner product for cosine similarity
        self.index.add(embeddings)
        
    def retrieve_relevant_tables(self, query: str, k: int = 3,min_score: float = 0.25) -> List[Dict[str, Any]]:
        """
        Retrieve the most relevant tables based on the natural language query.
        """
        # Encode the query
        query_embedding = self.model.encode([query])
        query_embedding = query_embedding.astype('float32')
        faiss.normalize_L2(query_embedding)
        
        # Search for similar table descriptions
        scores, indices = self.index.search(query_embedding, k)
        
        # Get the relevant table descriptions
        relevant_tables = []
        for i in range(min(len(indices[0]), k)):
            idx = indices[0][i]
            if idx < len(self.table_descriptions):
                table_info = self.table_descriptions[idx].copy()
                table_info['similarity_score'] = float(scores[0][i])
                # print(table_info['similarity_score'])
                # if table_info['similarity_score'] >= min_score:
                #     relevant_tables.append(table_info)
                relevant_tables.append(table_info)
                
        return relevant_tables
    
    def add_custom_table_descriptions(self, custom_table_descriptions: List[Dict[str, Any]]):
        """
        Add custom table descriptions to the RAG system.
        """
        # Get current descriptions count
        initial_count = len(self.table_descriptions)
        
        # Add the new descriptions
        for custom_table in custom_table_descriptions:
            table_description = {
                'name': custom_table['name'],
                'columns': custom_table.get('columns', []),
                'primary_keys': custom_table.get('primary_keys', []),
                'foreign_keys': custom_table.get('foreign_keys', []),
                'is_custom': True  # Mark as custom
            }
            
            # Create a text description for the custom table
            text_description = f"Table '{custom_table['name']}' has "
            
            if table_description['columns']:
                text_description += f"{len(table_description['columns'])} columns: "
                for i, col in enumerate(table_description['columns']):
                    text_description += f"{col['name']} of type {col['type']}"
                    if col.get('primary_key'):
                        text_description += " (primary key)"
                    if col.get('nullable', True) == False:
                        text_description += " (not null)"
                    if i < len(table_description['columns']) - 1:
                        text_description += ", "
            
            # Add primary key information
            if table_description['primary_keys']:
                text_description += f". Primary keys: {', '.join(table_description['primary_keys'])}."
            
            # Add foreign key information
            if table_description['foreign_keys']:
                text_description += f". It has foreign keys: "
                for i, fk in enumerate(table_description['foreign_keys']):
                    text_description += f"'{fk['constrained_columns']}' references '{fk['referred_table']}.{fk['referred_columns']}'"
                    if i < len(table_description['foreign_keys']) - 1:
                        text_description += ", "
            
            table_description['text_description'] = text_description
            self.table_descriptions.append(table_description)
        
        # Rebuild the index to include new descriptions
        self._build_index()
        
        print(f"Added {len(custom_table_descriptions)} custom table descriptions. Total tables now: {len(self.table_descriptions)}")