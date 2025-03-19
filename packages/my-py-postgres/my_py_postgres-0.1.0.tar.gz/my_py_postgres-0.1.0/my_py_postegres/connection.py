"""Database connection management classes."""
import logging
import psycopg2
from typing import Optional

from .config import DatabaseConfig

# Configure logging
logger = logging.getLogger(__name__)

class ConnectionManager:
    """Manages database connections and basic connectivity operations."""
    
    def __init__(self, config: DatabaseConfig):
        """Initialize with database configuration."""
        self.config = config
        self.conn = None
        self.cur = None
        self.selected_db = None
    
    def connect(self, database: str = "postgres") -> Optional[psycopg2.extensions.connection]:
        """Connect to the specified database.
        
        Args:
            database: Database name to connect to
            
        Returns:
            Connection object if successful, None otherwise
        """
        try:
            # Log connection attempt with sanitized info (no password)
            connection_info = {
                "host": self.config.host,
                "user": self.config.user,
                "database": database,
            }
            logger.info(f"Attempting to connect to database: {connection_info}")
            
            conn = psycopg2.connect(
                host=self.config.host,
                user=self.config.user,
                password=self.config.password,
                database=database,
            )
            logger.info(f"Connected to database: {database}")
            return conn
        except psycopg2.OperationalError as e:
            logger.error(f"Connection error for {database}: {e}")
            return None
        except Exception as e:
            logger.error(f"Error connecting to database {database}: {e}")
            return None
    
    def setup_connection(self, database: str) -> bool:
        """Set up a connection to the specified database.
        
        Returns:
            True if connection was established successfully
        """
        self.close()  # Close any existing connection
        self.selected_db = database
        self.conn = self.connect(database)
        
        if self.conn:
            self.cur = self.conn.cursor()
            logger.info(f"Connection established to database: {database}")
            return True
        return False
    
    def is_connected(self) -> bool:
        """Check if the database connection is active."""
        if self.conn is None:
            return False
        
        try:
            # Simple query to test connection
            self.cur.execute("SELECT 1;")
            return True
        except Exception:
            return False
    
    def begin_transaction(self) -> bool:
        """Begin a transaction for multiple operations."""
        if self.conn:
            logger.info("Transaction started")
            return True
        return False
    
    def commit(self) -> bool:
        """Commit the current transaction."""
        if self.conn:
            self.conn.commit()
            logger.info("Transaction committed")
            return True
        return False
    
    def rollback(self) -> bool:
        """Roll back the current transaction."""
        if self.conn:
            self.conn.rollback()
            logger.info("Transaction rolled back")
            return True
        return False
    
    def close(self) -> None:
        """Close the database connection."""
        if self.cur:
            self.cur.close()
        if self.conn:
            self.conn.close()
            self.conn = None
            self.cur = None
            logger.info("Database connection closed.")


class Transaction:
    """Context manager for database transactions."""
    def __init__(self, db_manager):
        self.db_manager = db_manager

    def __enter__(self):
        self.db_manager.begin_transaction()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is not None:
            # An exception occurred, roll back
            self.db_manager.rollback()
        else:
            # No exception, commit
            self.db_manager.commit()
        return False  # Don't suppress exceptions