from typing import Any
import ast
from datetime import datetime

class Attribute:
    """Represents a field in a data object"""
    def __init__(self, name: str): 
        self.name: str = name.strip()

class Value:
    """Represents a value in a condition"""
    def __init__(self, name: str):
        self.name = name
        match name:
            case str():
                self.processed = self._convert_string(name.strip())
            case _:
                self.processed = self.name
    
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