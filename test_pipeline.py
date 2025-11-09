#!/usr/bin/env python3
"""
Test script for the Natural Language to SQL application.
This script creates a sample database and tests the complete pipeline.
"""
import os
import tempfile
from sqlalchemy import create_engine, text
from natural_language_to_sql.core.nsql_agent import NSQLAgent


def create_sample_database():
    """
    Create a sample database with test tables for demonstration.
    """
    # Create a temporary SQLite database
    temp_db = tempfile.NamedTemporaryFile(delete=False, suffix='.db')
    temp_db.close()
    
    engine = create_engine(f"sqlite:///{temp_db.name}")
    
    # Create sample tables
    with engine.connect() as conn:
        # Create customers table
        conn.execute(text("""
            CREATE TABLE customers (
                id INTEGER PRIMARY KEY,
                name TEXT NOT NULL,
                email TEXT,
                age INTEGER,
                city TEXT
            )
        """))
        
        # Create orders table
        conn.execute(text("""
            CREATE TABLE orders (
                id INTEGER PRIMARY KEY,
                customer_id INTEGER,
                product_name TEXT NOT NULL,
                quantity INTEGER,
                price REAL,
                order_date DATE,
                FOREIGN KEY (customer_id) REFERENCES customers (id)
            )
        """))
        
        # Insert sample data
        conn.execute(text("""
            INSERT INTO customers (id, name, email, age, city) VALUES
                (1, 'John Doe', 'john@example.com', 30, 'New York'),
                (2, 'Jane Smith', 'jane@example.com', 25, 'Los Angeles'),
                (3, 'Bob Johnson', 'bob@example.com', 35, 'Chicago')
        """))
        
        conn.execute(text("""
            INSERT INTO orders (id, customer_id, product_name, quantity, price, order_date) VALUES
                (1, 1, 'Laptop', 1, 999.99, '2023-01-15'),
                (2, 1, 'Mouse', 2, 25.99, '2023-02-20'),
                (3, 2, 'Keyboard', 1, 79.99, '2023-03-10'),
                (4, 3, 'Monitor', 1, 299.99, '2023-04-05')
        """))
        
        conn.commit()
    
    return f"sqlite:///{temp_db.name}", engine


def test_pipeline():
    """
    Test the complete Natural Language to SQL pipeline.
    """
    # Create sample database
    db_url, engine = create_sample_database()
    print(f"Created sample database at: {db_url}")
    
    # Define custom table descriptions for testing
    custom_table_descriptions = [
        {
            "name": "employees",
            "columns": [
                {
                    "name": "id",
                    "type": "INTEGER",
                    "nullable": False,
                    "primary_key": True
                },
                {
                    "name": "name",
                    "type": "TEXT",
                    "nullable": False
                },
                {
                    "name": "department_id",
                    "type": "INTEGER",
                    "nullable": True,
                    "foreign_key": True
                },
                {
                    "name": "salary",
                    "type": "REAL",
                    "nullable": True
                }
            ],
            "primary_keys": ["id"],
            "foreign_keys": [
                {
                    "constrained_columns": ["department_id"],
                    "referred_table": "departments",
                    "referred_columns": ["id"]
                }
            ]
        },
        {
            "name": "departments",
            "columns": [
                {
                    "name": "id",
                    "type": "INTEGER",
                    "nullable": False,
                    "primary_key": True
                },
                {
                    "name": "name",
                    "type": "TEXT",
                    "nullable": False
                },
                {
                    "name": "location",
                    "type": "TEXT",
                    "nullable": True
                }
            ],
            "primary_keys": ["id"]
        }
    ]
    
    # Set up the NSQL agent with custom table descriptions
    try:
        agent = NSQLAgent(db_url, custom_table_descriptions)
    except ValueError as e:
        print(f"Error initializing agent: {e}")
        print("Make sure GEMINI_API_KEY environment variable is set.")
        return
    
    # Test queries
    test_queries = [
        "Show all customers",
        "What are the names and emails of all customers?",
        "Find all orders with price greater than 50",
        "Show customer names and their order products",
        "What is the total quantity of all orders?"
    ]
    
    print("\n" + "="*60)
    print("TESTING NATURAL LANGUAGE TO SQL PIPELINE")
    print("="*60)
    
    for i, query in enumerate(test_queries, 1):
        print(f"\nTest {i}: {query}")
        print("-" * 40)
        
        try:
            result = agent.process_query(query)
            print(result)
        except Exception as e:
            print(f"Error processing query: {e}")
    
    print("\n" + "="*60)
    print("TESTING COMPLETED")
    print("="*60)


if __name__ == "__main__":
    test_pipeline()