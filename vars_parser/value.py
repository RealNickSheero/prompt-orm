from typing import Any
from dataclasses import dataclass
import ast
from datetime import datetime

class Value:
    """Represents a value in a condition"""
    def __init__(self, name: str):
        self.name: str = name.strip()
        self.processed: Any = self._convert_string(self.name)
    
    @staticmethod
    def _convert_string(s: str) -> Any:
        """Convert string to appropriate type"""
        # Try Python literal first
        try:
            return ast.literal_eval(s)
        except (ValueError, SyntaxError, NameError):
            # Try datetime next
            try:
                return datetime.fromisoformat(s)
            except ValueError:
                # Return as string if nothing else works
                return s
    
    def get_value(self) -> Any:
        """Get the raw value"""
        return self.processed