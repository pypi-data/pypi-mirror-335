"""SQL query building utilities."""
from typing import List, Dict, Any, Tuple, Optional

class QueryBuilder:
    """Utility class for building SQL queries with proper parameter handling."""
    
    @staticmethod
    def build_select(table_name: str, columns: List[str] = None, 
                    conditions: Dict[str, Any] = None, limit: int = None) -> Tuple[str, List]:
        """Build a SELECT query with parameters.
        
        Args:
            table_name: Table name to select from
            columns: Columns to select (None for all)
            conditions: WHERE conditions as dict
            limit: Results limit
            
        Returns:
            Tuple of (query_string, parameters)
        """
        cols = "*" if not columns else ", ".join(columns)
        query = f"SELECT {cols} FROM {table_name}"
        params = []
        
        if conditions:
            where_clauses = [f"{col} = %s" for col in conditions.keys()]
            query += f" WHERE {' AND '.join(where_clauses)}"
            params.extend(conditions.values())
        
        if limit:
            query += f" LIMIT {limit}"
            
        return query, params
    
    @staticmethod
    def build_advanced_select(
        table_name: str, 
        columns: List[str] = None,
        where: str = None,
        params: List = None,
        group_by: str = None,
        order_by: str = None,
        limit: int = None,
        offset: int = None
    ) -> Tuple[str, List]:
        """Build an advanced SELECT query with parameters.
        
        Returns:
            Tuple of (query_string, parameters)
        """
        cols = "*" if not columns else ", ".join(columns)
        query = f"SELECT {cols} FROM {table_name}"
        final_params = [] if params is None else params
        
        if where:
            query += f" WHERE {where}"
        
        if group_by:
            query += f" GROUP BY {group_by}"
        
        if order_by:
            query += f" ORDER BY {order_by}"
        
        if limit:
            query += f" LIMIT {limit}"
        
        if offset:
            query += f" OFFSET {offset}"
            
        return query, final_params
    
    @staticmethod
    def build_insert(table_name: str, data: Dict[str, Any]) -> Tuple[str, List]:
        """Build an INSERT query with parameters.
        
        Returns:
            Tuple of (query_string, parameters)
        """
        columns = list(data.keys())
        values = list(data.values())
        placeholders = ["%s"] * len(values)
        
        query = f"INSERT INTO {table_name} ({', '.join(columns)}) VALUES ({', '.join(placeholders)});"
        
        return query, values
    
    @staticmethod
    def build_update(table_name: str, data: Dict[str, Any], 
                    conditions: Dict[str, Any]) -> Tuple[str, List]:
        """Build an UPDATE query with parameters.
        
        Returns:
            Tuple of (query_string, parameters)
        """
        set_clauses = [f"{col} = %s" for col in data.keys()]
        where_clauses = [f"{col} = %s" for col in conditions.keys()]
        
        query = f"UPDATE {table_name} SET {', '.join(set_clauses)} WHERE {' AND '.join(where_clauses)}"
        params = list(data.values()) + list(conditions.values())
        
        return query, params
    
    @staticmethod
    def build_delete(table_name: str, conditions: Dict[str, Any]) -> Tuple[str, List]:
        """Build a DELETE query with parameters.
        
        Returns:
            Tuple of (query_string, parameters)
        """
        where_clauses = [f"{col} = %s" for col in conditions.keys()]
        query = f"DELETE FROM {table_name} WHERE {' AND '.join(where_clauses)}"
        params = list(conditions.values())
        
        return query, params
    
    @staticmethod
    def build_create_table(table_name: str, columns: Dict[str, str], 
                          primary_key: Optional[str] = None) -> str:
        """Build a CREATE TABLE query.
        
        Returns:
            Query string (no parameters needed)
        """
        columns_list = []
        for col_name, col_type in columns.items():
            if col_name == primary_key:
                columns_list.append(f"{col_name} {col_type} PRIMARY KEY")
            else:
                columns_list.append(f"{col_name} {col_type}")

        columns_str = ", ".join(columns_list)
        return f"CREATE TABLE IF NOT EXISTS {table_name} ({columns_str});"