"""
Utility functions for the Natural Language to SQL application.
"""
import os
import re
from typing import Optional


def get_env_variable(var_name: str, default: Optional[str] = None) -> str:
    """
    Get an environment variable or return a default value.
    """
    value = os.getenv(var_name)
    if value is None:
        if default is not None:
            return default
        else:
            raise ValueError(f"Environment variable {var_name} is required but not set")
    return value


def validate_sql_query(sql_query: str) -> bool:
    """
    Basic validation of SQL query to prevent potentially dangerous operations.
    This is a simple implementation - in production, use a proper SQL parser.
    """
    # Convert to lowercase for case-insensitive matching
    query_lower = sql_query.lower().strip()
    
    # Dangerous SQL commands that could modify data or schema
    dangerous_keywords = [
        'drop', 'delete', 'truncate', 'alter', 'create', 'insert', 'update',
        'grant', 'revoke', 'commit', 'rollback', 'savepoint', 'merge'
    ]
    
    # Check for dangerous keywords but allow "select" and other safe operations
    for keyword in dangerous_keywords:
        # Use word boundaries to avoid partial matches
        if re.search(r'\b' + re.escape(keyword) + r'\b', query_lower):
            return False
    
    # Additional checks could be added here:
    # - Check for SQL injection patterns
    # - Validate that the query only contains SELECT statements
    
    return True


def sanitize_sql_query(sql_query: str) -> str:
    """
    Sanitize the SQL query to remove potentially harmful elements.
    """
    # Remove any semicolons that might allow multiple statements
    # (Though multiple statements could be part of a legitimate query)
    sanitized = sql_query.strip()
    
    # Remove trailing semicolon if it exists (we'll add it back later if needed)
    if sanitized.endswith(';'):
        sanitized = sanitized[:-1]
    
    # Remove any multi-statement attempts
    if ';' in sanitized[:-1]:  # If semicolon exists not at the end
        statements = sanitized.split(';')
        # Only allow the first statement for safety
        sanitized = statements[0].strip()
    
    return sanitized


def validate_and_sanitize_query(sql_query: str) -> tuple[bool, str]:
    """
    Validate and sanitize the SQL query.
    Returns a tuple: (is_valid, sanitized_query)
    """
    # First sanitize the query
    sanitized_query = sanitize_sql_query(sql_query)
    
    # Then validate
    is_valid = validate_sql_query(sanitized_query)
    
    return is_valid, sanitized_query