#!/usr/bin/env python3
"""
Simple example to test the Natural Language to SQL application with an existing SQLite database.
"""
import os
import sqlite3
import tempfile
from natural_language_to_sql.core.nsql_agent import NSQLAgent


def create_test_database():
    """Create a simple test database with sample data."""
    # Create a temporary SQLite database file
    db_fd, db_path = tempfile.mkstemp(suffix='.db')
    os.close(db_fd)
    
    # Connect to the database
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Create a sample table
    cursor.execute('''
        CREATE TABLE employees (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            department TEXT,
            salary REAL
        )
    ''')
    
    # Insert sample data
    sample_data = [
        (1, 'Alice Johnson', 'Engineering', 75000),
        (2, 'Bob Smith', 'Marketing', 65000),
        (3, 'Carol Davis', 'Engineering', 80000),
        (4, 'David Wilson', 'Sales', 60000),
        (5, 'Eva Brown', 'Marketing', 68000)
    ]
    
    cursor.executemany('INSERT INTO employees VALUES (?, ?, ?, ?)', sample_data)
    
    # Commit and close
    conn.commit()
    conn.close()
    
    return db_path


def main():
    # Create the test database
    db_path = create_test_database()
    print(f"Created test database at: {db_path}")
    
    # Create the NSQL agent
    try:
        agent = NSQLAgent(f"sqlite:///{db_path}")
    except ValueError as e:
        print(f"Error initializing agent: {e}")
        print("Make sure GEMINI_API_KEY environment variable is set.")
        return
    
    # Example queries
    queries = [
        "Show all employees",
        "What are the names of all employees in the Engineering department?",
        "Find employees with salary greater than 70000",
        "How many employees are in the Marketing department?"
    ]
    
    print("\nTesting queries on the database:")
    print("="*50)
    
    for i, query in enumerate(queries, 1):
        print(f"\nQuery {i}: {query}")
        print("-" * 30)
        try:
            result = agent.process_query(query)
            print(result)
        except Exception as e:
            print(f"Error: {e}")
    
    print("\n" + "="*50)
    
    # Clean up
    os.remove(db_path)
    print(f"Cleaned up test database: {db_path}")


if __name__ == "__main__":
    main()