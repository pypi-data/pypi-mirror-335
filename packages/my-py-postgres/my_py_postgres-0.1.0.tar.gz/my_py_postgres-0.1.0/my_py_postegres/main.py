"""Main database manager coordinator."""
import logging
from typing import List, Dict, Any, Optional, Tuple

from .config import DatabaseConfig
from .connection import ConnectionManager, Transaction
from .schema import SchemaManager
from .data_manager import DataManager

# Configure logging
logger = logging.getLogger(__name__)

class DatabaseManager:
    """Coordinator class that manages database operations through specialized components."""
    
    def __init__(self, config=None):
        """Initialize the DatabaseManager and create component objects."""
        # Use provided config or create default
        self.config = config or DatabaseConfig()
        
        # Create component managers
        self.connection_manager = ConnectionManager(self.config)
        self.schema_manager = SchemaManager(self.connection_manager)
        self.data_manager = DataManager(self.connection_manager, self.schema_manager)
        
        # Internal state
        self.selected_db = None
        self.available_dbs = self.schema_manager.list_databases()

    def __enter__(self):
        """Support for context manager protocol."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Close connections when exiting the context."""
        self.close()
        return False  # Don't suppress exceptions

    def setup(self):
        """Set up a connection to the selected database."""
        if self.connection_manager.setup_connection(self.selected_db):
            logger.info(f"Connection established to database: {self.selected_db}")
            return True
        return False

    def _refresh_available_dbs(self) -> List[str]:
        """Refresh the list of available databases."""
        self.available_dbs = self.schema_manager.list_databases()
        return self.available_dbs

    # --- Delegate methods to component managers ---
    
    def is_connected(self) -> bool:
        """Check if the database connection is active."""
        return self.connection_manager.is_connected()
    
    def begin_transaction(self):
        """Begin a transaction for multiple operations."""
        return self.connection_manager.begin_transaction()
    
    def commit(self):
        """Commit the current transaction."""
        return self.connection_manager.commit()
    
    def rollback(self):
        """Roll back the current transaction."""
        return self.connection_manager.rollback()
    
    def close(self):
        """Close the database connection."""
        return self.connection_manager.close()
    
    def get_dbs(self) -> List[str]:
        """Get all available databases."""
        return self.schema_manager.list_databases()
    
    def create_database(self):
        """Create a new PostgreSQL database."""
        db_name = input("Enter name for the new database: ")
        
        if self.schema_manager.create_database(db_name):
            self.available_dbs = self._refresh_available_dbs()
            self.selected_db = db_name
            self.setup()
    
    def show_tables(self) -> List[str]:
        """List all tables in the currently selected database."""
        return self.schema_manager.list_tables()
    
    def get_table_schema(self, table_name: str) -> List[Dict]:
        """Get the schema of a table."""
        return self.schema_manager.get_table_schema(table_name)
    
    def _validate_column_names(self, table_name: str, columns: List[str]) -> bool:
        """Validate that column names exist in the table."""
        return self.schema_manager.validate_column_names(table_name, columns)
    
    def _check_table_columns(self, table_name: str, data_dict: Dict[str, Any], 
                            error_context: str) -> Tuple[bool, Optional[str]]:
        """Common validation for column names in dictionary keys."""
        return self.data_manager._check_table_columns(table_name, data_dict, error_context)
    
    def create_table(self):
        """Interactively create a new table in the selected database."""
        if not self.is_connected():
            logger.error("Not connected to any database")
            return False, "Not connected to any database"
            
        table_name = input("Enter the name of the table: ")
        number_of_columns = int(input("Enter the number of columns: "))

        columns = {}
        primary_key = None
        
        for i in range(1, number_of_columns + 1):
            column_name = input(f"Enter the name of column {i}: ")
            data_type = input(f"Enter the data type of column {i}: ")
            columns[column_name] = data_type
            
            if primary_key is None and input(f"Is this a primary key? (y/n): ").lower() == 'y':
                primary_key = column_name

        return self.schema_manager.create_table(table_name, columns, primary_key)
    
    def create_table_programmatic(self, table_name: str, columns: Dict[str, str], 
                                primary_key: Optional[str] = None) -> Tuple[bool, str]:
        """Create a table programmatically."""
        return self.schema_manager.create_table(table_name, columns, primary_key)
    
    def insert(self, table_name: str, data: Dict[str, Any]) -> Tuple[bool, str]:
        """Insert a record into a table."""
        return self.data_manager.insert(table_name, data)
    
    def insert_many(self, table_name: str, columns: List[str], 
                   values_list: List[List[Any]]) -> Tuple[bool, str]:
        """Insert multiple records into a table."""
        return self.data_manager.insert_many(table_name, columns, values_list)
    
    def select(self, table_name: str, columns: List[str] = None, 
              conditions: Dict[str, Any] = None, limit: int = None) -> List[Dict[str, Any]]:
        """Select records from a table."""
        return self.data_manager.select(table_name, columns, conditions, limit)
    
    def advanced_select(self, table_name: str, columns: List[str] = None, 
                       where: str = None, params: List[Any] = None, 
                       order_by: str = None, group_by: str = None,
                       limit: int = None, offset: int = None) -> List[Dict[str, Any]]:
        """Advanced select with more query options."""
        return self.data_manager.advanced_select(
            table_name, columns, where, params, order_by, group_by, limit, offset
        )
    
    def update(self, table_name: str, data: Dict[str, Any], 
              conditions: Dict[str, Any]) -> Tuple[bool, str]:
        """Update records in a table."""
        return self.data_manager.update(table_name, data, conditions)
    
    def delete(self, table_name: str, conditions: Dict[str, Any]) -> Tuple[bool, str]:
        """Delete records from a table."""
        return self.data_manager.delete(table_name, conditions)
    
    def execute_raw_query(self, query: str, params: List = None) -> Tuple[bool, Any]:
        """Execute a raw SQL query."""
        return self.data_manager.execute_raw_query(query, params)
    
    def batch_operations(self, operations: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Execute multiple operations in a single transaction."""
        if not self.is_connected():
            return [{'success': False, 'message': "Not connected to any database"}]
            
        results = []
        
        # Use transaction context manager
        with Transaction(self):
            for op in operations:
                op_type = op.get('type')
                table = op.get('table')
                data = op.get('data', {})
                conditions = op.get('conditions', {})
                
                result = None
                if op_type == 'insert':
                    result = self.insert(table, data)
                elif op_type == 'update':
                    result = self.update(table, data, conditions)
                elif op_type == 'delete':
                    result = self.delete(table, conditions)
                else:
                    result = (False, f"Invalid operation type: {op_type}")
                
                results.append({
                    'operation': op_type,
                    'table': table,
                    'success': result[0] if result else False,
                    'message': result[1] if result else "Invalid operation"
                })
                
                # If any operation fails, the whole transaction will roll back
                if result and not result[0]:
                    break
                    
        return results
    
    def init(self):
        """Initialize the database manager and prompt the user to select or create a database."""
        if not self.available_dbs:
            self.available_dbs = self._refresh_available_dbs()

        if not self.available_dbs:
            logger.warning("No databases found or cannot connect to PostgreSQL server.")
            choice = input("Would you like to create a new database? (y/n): ")
            if choice.lower() == "y":
                self.create_database()
            return

        print(f"Welcome to the Database Manager\nAvailable databases:\n{self.available_dbs}")
        database = input('Enter the name of the database (or type "new" to create a new one): ')

        if database.lower() == "new":
            self.create_database()
        elif database in self.available_dbs:
            logger.info(f"Selected database: {database}")
            self.selected_db = database
            self.setup()
        else:
            logger.warning(f"Database not found: {database}")

# Entry point
if __name__ == "__main__":
    from .cli import DatabaseCLI
    
    # Use the CLI interface
    cli = DatabaseCLI()
    cli.start()