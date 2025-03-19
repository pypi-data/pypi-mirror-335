"""PostgreSQL database management system with a user-friendly interface."""

from .config import DatabaseConfig
from .connection import ConnectionManager, Transaction
from .schema import SchemaManager
from .data_manager import DataManager
from .query_builder import QueryBuilder
from .colors import Colors
from .pretty_printer import PrettyPrinter
from .cli import DatabaseCLI

# Import main class for convenience
from .main import DatabaseManager

__all__ = [
    'DatabaseManager',
    'DatabaseConfig',
    'ConnectionManager', 
    'Transaction',
    'SchemaManager',
    'DataManager',
    'QueryBuilder',
    'Colors',
    'PrettyPrinter',
    'DatabaseCLI'
]