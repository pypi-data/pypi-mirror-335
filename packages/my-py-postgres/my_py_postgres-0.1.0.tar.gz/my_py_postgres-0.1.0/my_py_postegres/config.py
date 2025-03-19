"""Configuration manager for database connections."""
import os
import logging
from dotenv import load_dotenv 

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DatabaseConfig:
    """Configuration manager for database connections."""
    def __init__(self, env_file=None):
        """Initialize with optional environment file."""
        if env_file:
            load_dotenv(env_file)
        else:
            load_dotenv()  # Load from default .env
        
        self.host = os.getenv("DB_HOST", "localhost")
        self.user = os.getenv("DB_USER", "superuser")
        self.password = os.getenv("DB_PASSWORD", "aza")
        self.default_db = os.getenv("DB_NAME", "postgres")
        
        # Validate required configuration
        self._validate_config()
    
    def _validate_config(self):
        """Ensure all required configuration is present."""
        if not self.password:
            logger.warning("No database password set. This might cause connection issues.")
    
    def get_connection_params(self, database=None):
        """Get connection parameters as a dictionary."""
        return {
            "host": self.host,
            "user": self.user,
            "password": self.password,
            "database": database or self.default_db
        }