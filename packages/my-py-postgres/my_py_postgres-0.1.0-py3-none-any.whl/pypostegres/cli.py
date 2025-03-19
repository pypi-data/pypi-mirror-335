"""Command-line interface for the database manager."""
import logging
from typing import Optional

from .colors import Colors
from .pretty_printer import PrettyPrinter
from .main import DatabaseManager

# Configure logging
logger = logging.getLogger(__name__)

class DatabaseCLI:
    """Command Line Interface for DatabaseManager."""
    def __init__(self, db_manager=None):
        """Initialize with an optional DatabaseManager."""
        self.db_manager = db_manager or DatabaseManager()
    
    def start(self):
        """Start the CLI interface."""
        print("Welcome to the Database CLI")
        self.prompt_select_database()
        
        # Command loop
        while True:
            self.show_menu()
            choice = input("> ")
            if choice.lower() == "exit":
                break
            self.handle_command(choice)
        
        # Close connection when done
        self.db_manager.close()
            
    def prompt_select_database(self):
        """Prompt user to select or create a database."""
        dbs = self.db_manager.available_dbs
        if not dbs:
            print(f"{Colors.YELLOW}No databases available.{Colors.RESET}")
            if self._yes_no("Create a new database?"):
                self.create_database()
            return
        
        # Use pretty printer for databases
        PrettyPrinter.print_databases(dbs)
        
        db_name = input(f"{Colors.BRIGHT_GREEN}Select database (or type 'new' to create): {Colors.RESET}")
        
        if (db_name.lower() == "new"):
            self.create_database()
        elif db_name.isdigit() and 1 <= int(db_name) <= len(dbs):
            # Allow selection by number
            db_name = dbs[int(db_name) - 1]
            self.db_manager.selected_db = db_name
            self.db_manager.setup()
            print(f"{Colors.BRIGHT_GREEN}Connected to database: {db_name}{Colors.RESET}")
        elif db_name in dbs:
            self.db_manager.selected_db = db_name
            self.db_manager.setup()
            print(f"{Colors.BRIGHT_GREEN}Connected to database: {db_name}{Colors.RESET}")
        else:
            print(f"{Colors.RED}Database {db_name} not found.{Colors.RESET}")
    
    def show_menu(self):
        """Show the main menu."""
        db_name = self.db_manager.selected_db or "Not connected"
        print(f"\n{Colors.BOLD}{Colors.BRIGHT_BLUE}Database:{Colors.RESET} {Colors.BRIGHT_GREEN}{db_name}{Colors.RESET}")
        print(f"\n{Colors.BOLD}{Colors.WHITE}Database Operations:{Colors.RESET}")
        menu_items = [
            "List tables",
            "Create table",
            "Insert data",
            "Query data",
            "Update data",
            "Delete data",
            "Execute custom SQL",
            "Switch database"
        ]
        
        for i, item in enumerate(menu_items, 1):
            print(f"{Colors.BRIGHT_CYAN}{i}.{Colors.RESET} {item}")
            
        print(f"{Colors.BRIGHT_RED}exit:{Colors.RESET} Exit the program")
    
    def handle_command(self, choice):
        """Handle user command."""
        if not self.db_manager.is_connected():
            print("Not connected to a database.")
            self.prompt_select_database()
            return
            
        if choice == "1":
            self.list_tables()
        elif choice == "2":
            self.create_table()
        elif choice == "3":
            self.insert_data()
        elif choice == "4":
            self.query_data()
        elif choice == "5":
            self.update_data()
        elif choice == "6":
            self.delete_data()
        elif choice == "7":
            self.execute_custom_sql()
        elif choice == "8":
            self.prompt_select_database()
        else:
            print("Invalid choice")
    
    def create_database(self):
        """Create a new database."""
        self.db_manager.create_database()
    
    def list_tables(self):
        """List all tables with pretty formatting."""
        tables = self.db_manager.show_tables()
        PrettyPrinter.print_tables(tables)
    
    def create_table(self):
        """Create a new table."""
        self.db_manager.create_table()
    
    def insert_data(self):
        """Insert data into a table."""
        table = input("Table name: ")
        
        # Get table schema to know what columns to ask for
        schema = self.db_manager.get_table_schema(table)
        if not schema:
            print(f"Table '{table}' not found or has no columns")
            return
            
        data = {}
        for column in schema:
            col_name = column['column_name']
            value = input(f"Enter value for {col_name} ({column['data_type']}): ")
            
            # Skip empty values for nullable columns
            if not value and column['is_nullable'] == 'YES':
                continue
                
            # Convert value based on data type (simple conversion)
            if 'int' in column['data_type']:
                try:
                    value = int(value)
                except ValueError:
                    print(f"Invalid integer: {value}")
                    return
            
            data[col_name] = value
        
        success, message = self.db_manager.insert(table, data)
        print(message)
    
    def query_data(self):
        """Query data from a table with pretty output."""
        # Get the table name
        table = self._prompt_select_table("Query from which table?")
        if not table:
            return
            
        # Get schema to show available columns
        schema = self.db_manager.get_table_schema(table)
        if not schema:
            print(f"Could not retrieve schema for table '{table}'")
            return
            
        # Show available columns
        print(f"Available columns: {[col['column_name'] for col in schema]}")
        
        # Ask for columns to select
        columns_input = input("Enter column names to select (comma-separated, or * for all): ")
        columns = None
        if columns_input != "*":
            columns = [col.strip() for col in columns_input.split(",")]
        
        # Ask for conditions
        use_conditions = self._yes_no("Do you want to add WHERE conditions?")
        conditions = {}
        
        if use_conditions:
            print("Enter conditions (leave value empty to finish):")
            while True:
                col = input("Column name: ")
                if not col:
                    break
                    
                val = input(f"Value for {col}: ")
                if not val:
                    break
                    
                conditions[col] = val
        
        # Ask for limit
        limit_input = input("Enter result limit (or leave empty for no limit): ")
        limit = int(limit_input) if limit_input.strip() else None
        
        # Execute the query
        results = self.db_manager.select(table, columns, conditions, limit)
        
        # Display results
        if results:
            PrettyPrinter.print_records(results, f"Results from {table}")
        else:
            print(f"{Colors.YELLOW}No results found{Colors.RESET}")

    def update_data(self):
        """Update data in a table."""
        # Get the table name
        table = self._prompt_select_table("Update which table?")
        if not table:
            return
        
        # Get schema to show available columns
        schema = self.db_manager.get_table_schema(table)
        if not schema:
            print(f"Could not retrieve schema for table '{table}'")
            return
        
        # Ask for columns and values to update
        print("Enter new values (leave empty to finish):")
        data = {}
        while True:
            col = input("Column to update: ")
            if not col:
                break
                
            val = input(f"New value for {col}: ")
            if not val:
                break
                
            data[col] = val
        
        if not data:
            print("No update data provided")
            return
        
        # Ask for conditions
        print("Enter WHERE conditions (leave empty to finish):")
        conditions = {}
        while True:
            col = input("Condition column: ")
            if not col:
                break
                
            val = input(f"Value for {col}: ")
            if not val:
                break
                
            conditions[col] = val
        
        if not conditions:
            confirm = self._yes_no("Warning: No conditions specified. This will update ALL rows. Continue?")
            if not confirm:
                return
        
        # Execute the update
        success, message = self.db_manager.update(table, data, conditions)
        print(message)

    def delete_data(self):
        """Delete data from a table."""
        # Get the table name
        table = self._prompt_select_table("Delete from which table?")
        if not table:
            return
        
        # Ask for conditions
        print("Enter DELETE conditions (leave empty to finish):")
        conditions = {}
        while True:
            col = input("Condition column: ")
            if not col:
                break
                
            val = input(f"Value for {col}: ")
            if not val:
                break
                
            conditions[col] = val
        
        if not conditions:
            confirm = self._yes_no("WARNING: No conditions specified. This will DELETE ALL rows. Are you absolutely sure?")
            if not confirm:
                return
            
            # Double-check for dangerous operations
            confirm_again = self._yes_no(f"DANGER: You are about to delete ALL data from table '{table}'. Type 'yes' to confirm: ")
            if not confirm_again:
                return
        
        # Execute the delete
        success, message = self.db_manager.delete(table, conditions)
        print(message)

    def execute_custom_sql(self):
        """Execute a custom SQL query with pretty output."""
        print(f"{Colors.BRIGHT_CYAN}Enter custom SQL query (be careful with destructive operations):{Colors.RESET}")
        sql = input(f"{Colors.BRIGHT_GREEN}> {Colors.RESET}")
        
        if not sql.strip():
            return
        
        # Ask for parameters if needed
        use_params = self._yes_no("Do you want to add parameters?")
        params = []
        
        if use_params:
            print("Enter parameters (leave empty to finish):")
            while True:
                val = input("Parameter value: ")
                if not val:
                    break
                    
                params.append(val)
        
        # Execute the query
        success, result = self.db_manager.execute_raw_query(sql, params)
        
        if success:
            if isinstance(result, list):
                # Results from a SELECT query
                PrettyPrinter.print_records(result, "Query Results")
            else:
                # Message from a non-SELECT query
                print(f"{Colors.BRIGHT_GREEN}{result}{Colors.RESET}")
        else:
            print(f"{Colors.BRIGHT_RED}Error: {result}{Colors.RESET}")

    def _prompt_select_table(self, prompt_text="Select table:") -> Optional[str]:
        """Helper to prompt user to select a table with pretty formatting."""
        tables = self.db_manager.show_tables()
        
        if not tables:
            print(f"{Colors.YELLOW}No tables found in the current database.{Colors.RESET}")
            return None
        
        PrettyPrinter.print_tables(tables)
        
        choice = input(f"{Colors.BRIGHT_GREEN}Enter table number or name: {Colors.RESET}")
        
        # Handle numeric choice
        if choice.isdigit():
            idx = int(choice) - 1
            if 0 <= idx < len(tables):
                return tables[idx]
        
        # Handle table name
        if choice in tables:
            return choice
        
        print(f"{Colors.RED}Invalid selection: {choice}{Colors.RESET}")
        return None
    
    def _yes_no(self, question):
        """Ask a yes/no question."""
        return input(f"{question} (y/n): ").lower() == "y"