"""Data manipulation operations for database tables."""
import logging
from typing import List, Dict, Any, Tuple, Optional

from .connection import ConnectionManager
from .schema import SchemaManager
from .query_builder import QueryBuilder

# Configure logging
logger = logging.getLogger(__name__)

class DataManager:
    """Handles data operations (CRUD) on database tables."""
    
    def __init__(self, conn_manager: ConnectionManager, schema_manager: SchemaManager):
        """Initialize with connection and schema managers."""
        self.conn_manager = conn_manager
        self.schema_manager = schema_manager
    
    def _check_table_columns(self, table_name: str, data_dict: Dict[str, Any], 
                            error_context: str) -> Tuple[bool, Optional[str]]:
        """Common validation for column names in dictionary keys."""
        columns = list(data_dict.keys())
        if not self.schema_manager.validate_column_names(table_name, columns):
            error_msg = f"Invalid column names in {error_context}"
            logger.warning(error_msg)
            return False, error_msg
        return True, None
    
    def insert(self, table_name: str, data: Dict[str, Any]) -> Tuple[bool, str]:
        """Insert a record into a table."""
        if not self.conn_manager.is_connected():
            return False, "Not connected to any database"
            
        # Validate column names
        valid, error = self._check_table_columns(table_name, data, "insert data")
        if not valid:
            return False, error
            
        # Build and execute query
        query, params = QueryBuilder.build_insert(table_name, data)
        
        try:
            self.conn_manager.cur.execute(query, params)
            self.conn_manager.commit()
            return True, "Record inserted successfully."
        except Exception as e:
            self.conn_manager.rollback()
            return False, f"Error inserting record: {e}"
    
    def insert_many(self, table_name: str, columns: List[str], 
                   values_list: List[List[Any]]) -> Tuple[bool, str]:
        """Insert multiple records into a table."""
        if not self.conn_manager.is_connected():
            return False, "Not connected to any database"
            
        # Validate column names
        if not self.schema_manager.validate_column_names(table_name, columns):
            return False, "Invalid column names"
            
        # Build query (for executemany, different from single insert)
        placeholders = ["%s"] * len(columns)
        query = f"INSERT INTO {table_name} ({', '.join(columns)}) VALUES ({', '.join(placeholders)});"
        
        try:
            self.conn_manager.cur.executemany(query, values_list)
            self.conn_manager.commit()
            return True, f"{len(values_list)} records inserted successfully."
        except Exception as e:
            self.conn_manager.rollback()
            return False, f"Error inserting records: {e}"
    
    def select(self, table_name: str, columns: List[str] = None, 
              conditions: Dict[str, Any] = None, limit: int = None) -> List[Dict[str, Any]]:
        """Select records from a table."""
        if not self.conn_manager.is_connected():
            logger.error("Not connected to any database")
            return []
            
        # Validate column names if specified
        if columns and not self.schema_manager.validate_column_names(table_name, columns):
            logger.warning("Invalid column names in select")
            return []
            
        # Validate conditions if specified
        if conditions:
            valid, error = self._check_table_columns(table_name, conditions, "select conditions")
            if not valid:
                return []
        
        # Build and execute query
        query, params = QueryBuilder.build_select(table_name, columns, conditions, limit)
        
        try:
            self.conn_manager.cur.execute(query, params)
            results = self.conn_manager.cur.fetchall()
            col_names = [desc[0] for desc in self.conn_manager.cur.description]
            return [dict(zip(col_names, row)) for row in results]
        except Exception as e:
            logger.error(f"Error selecting records: {e}")
            return []
    
    def advanced_select(self, table_name: str, columns: List[str] = None, 
                       where: str = None, params: List[Any] = None, 
                       order_by: str = None, group_by: str = None,
                       limit: int = None, offset: int = None) -> List[Dict[str, Any]]:
        """Advanced select with more query options."""
        if not self.conn_manager.is_connected():
            logger.error("Not connected to any database")
            return []
            
        # Validate column names if specified
        if columns and not self.schema_manager.validate_column_names(table_name, columns):
            logger.warning("Invalid column names in advanced_select")
            return []
        
        # Build and execute query
        query, query_params = QueryBuilder.build_advanced_select(
            table_name, columns, where, params, group_by, order_by, limit, offset
        )
        
        try:
            self.conn_manager.cur.execute(query, query_params)
            results = self.conn_manager.cur.fetchall()
            col_names = [desc[0] for desc in self.conn_manager.cur.description]
            return [dict(zip(col_names, row)) for row in results]
        except Exception as e:
            logger.error(f"Error in advanced select: {e}")
            return []
    
    def update(self, table_name: str, data: Dict[str, Any], 
              conditions: Dict[str, Any]) -> Tuple[bool, str]:
        """Update records in a table."""
        if not self.conn_manager.is_connected():
            return False, "Not connected to any database"
            
        # Validate column names
        valid, error = self._check_table_columns(table_name, data, "update data")
        if not valid:
            return False, error
            
        valid, error = self._check_table_columns(table_name, conditions, "update conditions")
        if not valid:
            return False, error
        
        # Build and execute query
        query, params = QueryBuilder.build_update(table_name, data, conditions)
        
        try:
            self.conn_manager.cur.execute(query, params)
            rows_affected = self.conn_manager.cur.rowcount
            self.conn_manager.commit()
            return True, f"{rows_affected} record(s) updated successfully."
        except Exception as e:
            self.conn_manager.rollback()
            return False, f"Error updating records: {e}"
    
    def delete(self, table_name: str, conditions: Dict[str, Any]) -> Tuple[bool, str]:
        """Delete records from a table."""
        if not self.conn_manager.is_connected():
            return False, "Not connected to any database"
            
        # Validate column names
        valid, error = self._check_table_columns(table_name, conditions, "delete conditions")
        if not valid:
            return False, error
        
        # Build and execute query
        query, params = QueryBuilder.build_delete(table_name, conditions)
        
        try:
            self.conn_manager.cur.execute(query, params)
            rows_affected = self.conn_manager.cur.rowcount
            self.conn_manager.commit()
            return True, f"{rows_affected} record(s) deleted successfully."
        except Exception as e:
            self.conn_manager.rollback()
            return False, f"Error deleting records: {e}"
    
    def execute_raw_query(self, query: str, params: List = None) -> Tuple[bool, Any]:
        """Execute a raw SQL query."""
        if not self.conn_manager.is_connected():
            return False, "Not connected to any database"
            
        try:
            self.conn_manager.cur.execute(query, params if params else [])

            if query.strip().upper().startswith("SELECT"):
                results = self.conn_manager.cur.fetchall()
                col_names = [desc[0] for desc in self.conn_manager.cur.description]
                return True, [dict(zip(col_names, row)) for row in results]

            self.conn_manager.commit()
            return True, f"Query executed successfully. {self.conn_manager.cur.rowcount} row(s) affected."
        except Exception as e:
            self.conn_manager.rollback()
            return False, f"Error executing query: {e}"