from typing import Any
import ast
from datetime import datetime

class ConditionMask:
    def __init__(self, source_name, mask):
        self.source_name = source_name
        self.mask = mask

class ConditionArgument:
    """Represents a value in a condition"""
    def __init__(self, value: Any):
        self.value = self._convert_string(value)
        match self.value:
            case str():
                obj, _, attr = self.value.partition('.')
                if attr:
                    self.object = "placeholder"
                    self.attribute = attr.strip()
                    self.processed = attr.strip()
                else:
                    self.object = None
                    self.attribute = obj
                    self.processed = self.value
            case _:
                self.processed = self.value
                self.object = None
                self.attribute = None
    
    @staticmethod
    def _convert_string(s: str) -> Any:
        """Convert string to appropriate type"""
        # Try Python literal first
        if isinstance(s, str):
            s = s.strip()
        try:
            result = ast.literal_eval(s)
            return result
        except (ValueError, SyntaxError, NameError, TypeError):
            # Try datetime next
            try:
                result = datetime.fromisoformat(s)
                return result
            except (ValueError, SyntaxError, NameError, TypeError):
                # Return as string if nothing else works
                return s