"""
Main entry point for the Natural Language to SQL CLI application.
"""
import argparse
import sys
import json
from ..utils.config_manager import config_manager


def main():
    parser = argparse.ArgumentParser(description='Natural Language to SQL Converter')
    
    # Add subparsers for different commands
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Configuration command
    config_parser = subparsers.add_parser('config', help='Configure database and table descriptions')
    config_parser.add_argument('--db-url', type=str, help='Database URL to set')
    config_parser.add_argument('--table-descriptions', type=str, help='Path to JSON file containing custom table descriptions')
    config_parser.add_argument('--show', action='store_true', help='Show current configuration')
    config_parser.add_argument('--reset', action='store_true', help='Reset configuration to defaults')
    
    # Query command
    query_parser = subparsers.add_parser('query', help='Run a natural language query')
    query_parser.add_argument('--db-url', type=str, help='Database URL (overrides config)')
    query_parser.add_argument('--query', type=str, required=True, help='Natural language query to convert to SQL')
    query_parser.add_argument('--table-descriptions', type=str, help='Path to JSON file containing custom table descriptions (overrides config)')
    
    # Interactive mode command
    interactive_parser = subparsers.add_parser('interactive', help='Run in interactive mode')
    interactive_parser.add_argument('--db-url', type=str, help='Database URL (overrides config)')
    interactive_parser.add_argument('--table-descriptions', type=str, help='Path to JSON file containing custom table descriptions (overrides config)')
    
    args = parser.parse_args()
    
    if args.command == 'config':
        handle_config_command(args)
    elif args.command == 'query':
        handle_query_command(args)
    elif args.command == 'interactive':
        handle_interactive_command(args)
    elif args.command is None:
        # No command provided, show help
        parser.print_help()
        sys.exit(1)
    else:
        parser.print_help()
        sys.exit(1)


def handle_config_command(args):
    """Handle the configuration command."""
    if args.show:
        # Show current configuration
        config = config_manager.get_config()
        print("Current Configuration:")
        print(f"  Database URL: {config.get('db_url', 'Not set')}")
        print(f"  Table Descriptions File: {config.get('table_descriptions_file', 'Not set')}")
        print(f"  Gemini Model: {config.get('gemini_model', 'Not set')}")
        return
    
    if args.reset:
        config_manager.reset_config()
        print("Configuration reset to defaults")
        return
    
    # Set configuration values if provided
    if args.db_url:
        config_manager.set_db_url(args.db_url)
        print(f"Database URL set to: {args.db_url}")
    
    if args.table_descriptions:
        config_manager.set_table_descriptions_file(args.table_descriptions)
        print(f"Table descriptions file set to: {args.table_descriptions}")
    
    # Save the configuration if any values were set
    if args.db_url or args.table_descriptions:
        if config_manager.save_config():
            print("Configuration saved successfully")
        else:
            print("Error saving configuration")


def handle_query_command(args):
    """Handle the query command."""
    from ..core.nsql_agent import NSQLAgent
    # Get configuration values, with command-line args taking precedence
    db_url = args.db_url or config_manager.get_db_url()
    table_descriptions_file = args.table_descriptions or config_manager.get_table_descriptions_file()
    
    if not db_url:
        print("Error: Database URL not provided and not configured. Use 'nsql config --db-url <url>' to set it.")
        sys.exit(1)
    
    # Load custom table descriptions if provided or configured
    custom_table_descriptions = []
    if table_descriptions_file:
        try:
            with open(table_descriptions_file, 'r') as f:
                custom_table_descriptions = json.load(f)
            print(f"Loaded {len(custom_table_descriptions)} custom table descriptions from {table_descriptions_file}")
        except Exception as e:
            print(f"Error loading table descriptions: {e}")
            sys.exit(1)
    
    # Initialize the NSQL agent
    agent = NSQLAgent(db_url=db_url, custom_table_descriptions=custom_table_descriptions)
    
    # Process the query
    result = agent.process_query(args.query)
    print(result)


def handle_interactive_command(args):
    """Handle the interactive command."""
    from ..core.nsql_agent import NSQLAgent
    # Get configuration values, with command-line args taking precedence
    db_url = args.db_url or config_manager.get_db_url()
    table_descriptions_file = args.table_descriptions or config_manager.get_table_descriptions_file()
    
    if not db_url:
        print("Error: Database URL not provided and not configured. Use 'nsql config --db-url <url>' to set it.")
        sys.exit(1)
    
    # Load custom table descriptions if provided or configured
    custom_table_descriptions = []
    if table_descriptions_file:
        try:
            with open(table_descriptions_file, 'r') as f:
                custom_table_descriptions = json.load(f)
            print(f"Loaded {len(custom_table_descriptions)} custom table descriptions from {table_descriptions_file}")
        except Exception as e:
            print(f"Error loading table descriptions: {e}")
            sys.exit(1)
    
    # Initialize the NSQL agent
    agent = NSQLAgent(db_url=db_url, custom_table_descriptions=custom_table_descriptions)
    
    run_interactive_mode(agent)


def run_interactive_mode(agent):
    """Run the application in interactive mode"""
    print("Natural Language to SQL Converter - Interactive Mode")
    print("Enter your natural language queries (type 'exit' to quit):")
    
    # Allow adding more table descriptions during interactive mode
    print("\nCommands: 'add-table' to add table descriptions, 'exit' to quit")
    
    while True:
        try:
            user_input = input("\n> ").strip()
            if user_input.lower() in ['exit', 'quit', 'q']:
                break
            elif user_input.lower() == 'add-table':
                add_table_descriptions_interactive(agent)
            elif user_input:
                result = agent.process_query(user_input)
                print(result)
        except KeyboardInterrupt:
            print("\nGoodbye!")
            break
        except EOFError:
            print("\nGoodbye!")
            break


def add_table_descriptions_interactive(agent):
    """Allow user to add table descriptions interactively"""
    print("Adding table descriptions. Enter 'done' when finished.")
    
    table_name = input("Table name: ").strip()
    if table_name.lower() == 'done':
        return
        
    columns_input = input("Columns (format: name:type,nullable:bool,primary_key:bool; e.g., id:INTEGER,False,True,name:TEXT,True,False): ").strip()
    if columns_input.lower() == 'done':
        return
    
    # Parse columns input
    columns = []
    for col_str in columns_input.split(';'):
        if col_str.strip():
            parts = col_str.split(',')
            if len(parts) >= 3:
                col_name, col_type, nullable_str = parts[0].split(':')
                nullable = nullable_str.lower() == 'true'
                
                primary_key = False
                if len(parts) >= 3 and ':' in parts[2]:
                    pk_name, pk_value = parts[2].split(':')
                    primary_key = pk_value.lower() == 'true'
                
                col_info = {
                    'name': col_name.strip(),
                    'type': col_type.strip(),
                    'nullable': nullable,
                    'primary_key': primary_key
                }
                columns.append(col_info)
    
    table_desc = {
        'name': table_name,
        'columns': columns
    }
    
    agent.add_custom_table_descriptions([table_desc])
    print(f"Added table description for {table_name}")


if __name__ == "__main__":
    main()