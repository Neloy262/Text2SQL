# Natural Language to SQL Application

This application converts natural language queries to SQL using Google's Gemini LLM and Retrieval Augmented Generation (RAG).

## Features

- Convert natural language to SQL queries
- Uses RAG system for better context retrieval
- Integrates with Google Gemini for advanced language understanding
- SQL validation and execution
- Command-line interface
- Support for custom table descriptions

## Prerequisites

- Python 3.12+
- Google Gemini API key
- Poetry for dependency management

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd <repository-name>
```

2. Install dependencies using Poetry:
```bash
poetry install
```

3. Set up environment variables:
```bash
export GEMINI_API_KEY='your-gemini-api-key-here'
```

## Usage

### Command Line Interface

The CLI now supports configuration commands to set database and table descriptions that persist between sessions.

#### Configuration

Set your database URL:
```bash
poetry run nsql config --db-url "sqlite:///path/to/your/database.db"
```

Set custom table descriptions:
```bash
poetry run nsql config --table-descriptions "/path/to/table_descriptions.json"
```

View current configuration:
```bash
poetry run nsql config --show
```

Reset configuration:
```bash
poetry run nsql config --reset
```

#### Running Queries

After configuration, run queries simply:
```bash
poetry run nsql query --query "Show all customers"
```

Or run in interactive mode:
```bash
poetry run nsql interactive
```

You can also override the configured values with command-line arguments:

```bash
poetry run nsql query --db-url "sqlite:///other/database.db" --query "Show all customers"
```

```bash
poetry run nsql interactive --table-descriptions "/path/to/other_descriptions.json"
```

Alternatively, you can still use the old format without configuration:

```bash
poetry run python -m natural_language_to_sql.cli.main query --db-url "sqlite:///path/to/your/database.db" --query "Show all customers"
```

### Programmatic Usage

```python
from natural_language_to_sql.core.nsql_agent import NSQLAgent

# Initialize the agent with your database URL
agent = NSQLAgent("sqlite:///path/to/your/database.db")

# Process a natural language query
result = agent.process_query("Show all customers")
print(result)
```

You can also provide custom table descriptions:

```python
from natural_language_to_sql.core.nsql_agent import NSQLAgent

# Define custom table descriptions
custom_descriptions = [
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
            }
        ],
        "primary_keys": ["id"]
    }
]

# Initialize the agent with custom table descriptions
agent = NSQLAgent(
    db_url="sqlite:///path/to/your/database.db",
    custom_table_descriptions=custom_descriptions
)

result = agent.process_query("Show all employees")
print(result)
```

### Table Descriptions Format

The table descriptions JSON should follow this format:

```json
[
  {
    "name": "table_name",
    "columns": [
      {
        "name": "column_name",
        "type": "DATA_TYPE",
        "nullable": true|false,
        "primary_key": true|false,
        "foreign_key": true|false
      }
    ],
    "primary_keys": ["col1", "col2"],
    "foreign_keys": [
      {
        "constrained_columns": ["col_name"],
        "referred_table": "other_table",
        "referred_columns": ["other_col"]
      }
    ]
  }
]
```

## Architecture

The application follows a modular architecture:

- `cli/` - Command-line interface components
- `core/` - Core logic including the main NSQL agent and RAG system
- `models/` - LLM integration (Google Gemini)
- `utils/` - Helper functions and utilities

### Key Components

1. **RAG System**: Retrieves relevant table information based on the natural language query
2. **Gemini LLM**: Generates SQL queries using the retrieved context
3. **SQL Validator**: Ensures generated queries are safe and only allow SELECT operations
4. **NSQL Agent**: Orchestrates the entire process

## Configuration

The application looks for the following environment variable:

- `GEMINI_API_KEY` - Your Google Gemini API key

## Example Queries

The system can handle various types of queries:

- "Show all customers"
- "What are the names and emails of all customers?"
- "Find all orders with price greater than 50"
- "Show customer names and their order products"

## Security

- Only SELECT queries are allowed to prevent data modification
- SQL validation to prevent injection attacks
- Input sanitization to prevent harmful operations

## Testing

Run the test pipeline:

```bash
python test_pipeline.py
```

This creates a sample database and runs test queries to validate the entire pipeline.