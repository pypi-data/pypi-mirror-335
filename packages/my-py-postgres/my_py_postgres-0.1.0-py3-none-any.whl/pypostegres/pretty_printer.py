"""Utility for pretty printing database objects."""
import shutil
from typing import List, Dict, Any

from .colors import Colors

class PrettyPrinter:
    """Utility for printing database objects in a colorful, formatted way."""
    
    @staticmethod
    def truncate(text, max_length=20):
        """Truncate text and add ellipsis if too long."""
        if text is None:
            return "NULL"
        text = str(text)
        if len(text) <= max_length:
            return text
        return text[:max_length-3] + "..."
    
    @staticmethod
    def get_terminal_width():
        """Get terminal width or default to 80."""
        try:
            return shutil.get_terminal_size().columns
        except:
            return 80
    
    @classmethod
    def print_title(cls, title):
        """Print a centered title with decoration."""
        term_width = cls.get_terminal_width()
        padding = (term_width - len(title) - 4) // 2
        print(f"\n{Colors.BRIGHT_BLUE}{'-' * padding} {Colors.BOLD}{Colors.WHITE}{title}{Colors.RESET}{Colors.BRIGHT_BLUE} {'-' * padding}{Colors.RESET}\n")
    
    @classmethod
    def print_databases(cls, databases):
        """Print a list of databases in a colorful way."""
        if not databases:
            print(f"{Colors.YELLOW}No databases found.{Colors.RESET}")
            return
        
        cls.print_title("Available Databases")
        
        # Calculate columns based on terminal width and longest db name
        max_name_len = max(len(db) for db in databases) + 2
        term_width = cls.get_terminal_width()
        cols = max(1, term_width // (max_name_len + 4))
        
        # Print databases in columns
        for i, db in enumerate(databases):
            if i > 0 and i % cols == 0:
                print()  # New line
            
            # Alternate colors for visual separation
            color = Colors.BRIGHT_GREEN if i % 2 == 0 else Colors.BRIGHT_CYAN
            print(f"{color}[{i+1:2d}] {db}{Colors.RESET}", end=" " * (max_name_len - len(db)))
            
        print("\n")
    
    @classmethod
    def print_tables(cls, tables):
        """Print a list of tables with decoration."""
        if not tables:
            print(f"{Colors.YELLOW}No tables found in the current database.{Colors.RESET}")
            return
        
        cls.print_title("Tables")
        
        # Calculate columns similar to databases
        max_name_len = max(len(table) for table in tables) + 2
        term_width = cls.get_terminal_width()
        cols = max(1, term_width // (max_name_len + 4))
        
        for i, table in enumerate(tables):
            if i > 0 and i % cols == 0:
                print()  # New line
            
            # Color tables with alternating colors
            color = Colors.MAGENTA if i % 2 == 0 else Colors.BRIGHT_MAGENTA
            print(f"{color}[{i+1:2d}] {table}{Colors.RESET}", end=" " * (max_name_len - len(table)))
        
        print("\n")
    
    @classmethod
    def print_records(cls, records, title=None, max_width=20):
        """Print database records in a pretty table format with truncated values.
        
        Args:
            records: List of dictionaries representing database records
            title: Optional title for the results
            max_width: Maximum width for each column
        """
        if not records:
            print(f"{Colors.YELLOW}No records found.{Colors.RESET}")
            return
        
        if title:
            cls.print_title(title)
        
        # Get headers and determine column widths
        headers = list(records[0].keys())
        col_widths = {}
        
        for header in headers:
            # Width is the min of max_width and the max length of values (+2 for padding)
            header_len = len(str(header))
            max_value_len = max(len(str(record.get(header, ''))) for record in records)
            col_widths[header] = min(max_width, max(header_len, max_value_len)) + 2
        
        # Calculate total table width
        table_width = sum(col_widths.values()) + len(headers) + 1
        
        # Build border parts separately then combine with colors
        top_border = "┌" + "┬".join("─" * col_widths[h] for h in headers) + "┐"
        print(f"{Colors.BRIGHT_BLACK}{top_border}{Colors.RESET}")
        
        # Print header row
        header_row = "│"
        for h in headers:
            padded = str(h).center(col_widths[h])
            header_row += f"{Colors.BOLD}{Colors.WHITE}{padded}{Colors.RESET}│"
        print(header_row)
        
        # Build and print separator
        mid_border = "├" + "┼".join("─" * col_widths[h] for h in headers) + "┤"
        print(f"{Colors.BRIGHT_BLACK}{mid_border}{Colors.RESET}")
        
        # Print data rows
        for i, record in enumerate(records):
            row_color = Colors.BRIGHT_BLACK if i % 2 == 0 else ""
            row = "│"
            for h in headers:
                value = cls.truncate(record.get(h, ''), max_width)
                padded = str(value).ljust(col_widths[h])
                
                # Choose color based on data type
                if isinstance(record.get(h), (int, float)):
                    value_color = Colors.BRIGHT_CYAN
                elif record.get(h) is None:
                    value_color = Colors.BRIGHT_BLACK
                else:
                    value_color = Colors.BRIGHT_WHITE
                
                row += f"{row_color}{value_color}{padded}{Colors.RESET}│"
            print(row)
        
        # Build and print bottom border
        bottom_border = "└" + "┴".join("─" * col_widths[h] for h in headers) + "┘"
        print(f"{Colors.BRIGHT_BLACK}{bottom_border}{Colors.RESET}")
        print(f"{Colors.BRIGHT_GREEN}{len(records)} record(s){Colors.RESET}\n")