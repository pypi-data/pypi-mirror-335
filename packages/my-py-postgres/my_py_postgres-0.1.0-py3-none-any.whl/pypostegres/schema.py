import logging
from typing import List, Dict, Any, Tuple, Optional

from .connection import ConnectionManager
from .query_builder import QueryBuilder

# Configure logging
logger = logging.getLogger(__name__)

class SchemaManager:
    """Handles database schema operations like tables, columns, etc."""
    
    def __init__(self, conn_manager: ConnectionManager):
        """Initialize with connection manager."""
        self.conn_manager = conn_manager
    
    def list_databases(self) -> List[str]:
        """Get all available databases from the PostgreSQL server.
        
        Returns:
            A list of database names.
        """
        try:
            # Temporarily connect to postgres to get database list
            conn = self.conn_manager.connect()
            if not conn:
                return []

            with conn:
                with conn.cursor() as cur:
                    cur.execute("SELECT datname FROM pg_database WHERE datistemplate = false;")
                    databases = [db[0] for db in cur.fetchall()]

            logger.info(f"Fetched list of available databases: {len(databases)} found")
            return databases
        except Exception as e:
            logger.error(f"Error fetching databases: {e}")
            return []
    
    def create_database(self, db_name: str) -> bool:
        """Create a new database.
        
        Returns:
            True if created successfully
        """
        # Validate database name
        if not all(c.isalnum() or c == '_' for c in db_name):
            logger.error("Invalid database name. Use only alphanumeric characters and underscores.")
            return False
            
        try:
            # Connect to postgres to create a new database
            conn = self.conn_manager.connect()
            if not conn:
                return False

            conn.autocommit = True
            with conn.cursor() as cur:
                cur.execute(f"CREATE DATABASE {db_name};")
                
            logger.info(f"Database '{db_name}' created successfully.")
            return True
        except Exception as e:
            logger.error(f"Error creating database: {e}")
            return False
    
    def list_tables(self) -> List[str]:
        """List all tables in the currently selected database.
        
        Returns:
            List of table names
        """
        if not self.conn_manager.is_connected():
            logger.error("Not connected to any database")
            return []
            
        query = "SELECT table_name FROM information_schema.tables WHERE table_schema = 'public';"
        
        try:
            self.conn_manager.cur.execute(query)
            tables = [table[0] for table in self.conn_manager.cur.fetchall()]
            return tables
        except Exception as e:
            logger.error(f"Error listing tables: {e}")
            return []
    
    def get_table_schema(self, table_name: str) -> List[Dict]:
        """Get the schema of a table.
        
        Args:
            table_name: The name of the table.
            
        Returns:
            A list of dictionaries with column information.
        """
        if not self.conn_manager.is_connected():
            logger.error("Not connected to any database")
            return []
            
        query = """
            SELECT column_name, data_type, character_maximum_length, is_nullable
            FROM information_schema.columns
            WHERE table_name = %s AND table_schema = 'public'
            ORDER BY ordinal_position;
        """
        
        try:
            self.conn_manager.cur.execute(query, [table_name])
            columns = self.conn_manager.cur.fetchall()
            col_names = [desc[0] for desc in self.conn_manager.cur.description]
            return [dict(zip(col_names, col)) for col in columns]
        except Exception as e:
            logger.error(f"Error getting table schema: {e}")
            return []
    
    def validate_column_names(self, table_name: str, columns: List[str]) -> bool:
        """Validate that column names exist in the table."""
        schema = self.get_table_schema(table_name)
        valid_columns = [col["column_name"] for col in schema]
        return all(col in valid_columns for col in columns)
    
    def create_table(self, table_name: str, columns: Dict[str, str], 
                    primary_key: Optional[str] = None) -> Tuple[bool, str]:
        """Create a table.
        
        Returns:
            Tuple of (success, message)
        """
        if not self.conn_manager.is_connected():
            return False, "Not connected to any database"
        
        query = QueryBuilder.build_create_table(table_name, columns, primary_key)
        
        try:
            self.conn_manager.cur.execute(query)
            self.conn_manager.commit()
            return True, f"Table '{table_name}' created successfully."
        except Exception as e:
            self.conn_manager.rollback()
            return False, f"Error creating table: {e}"
