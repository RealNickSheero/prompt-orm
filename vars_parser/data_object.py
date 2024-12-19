from typing import Any, Optional, Dict
from dataclasses import dataclass
from .parser_base import ParseResult, Parser
from glom import glom #type: ignore

class DataObject:
    """Represents a data object"""
    potential_sources = {'state': None, 'obj': None}

    def __init__(self, expression):
        self.expression: str = expression
        self.source: str = None
        self.path: str = None
        self.remaining: str = None
        self.parsed: bool = self.parse()
        self.idx: int = 0
        self.value: Any = self.get_value()
    
    def parse(self):
        """Parse a data object from the expression string"""
        expression = self.expression.strip()
        for source in self.potential_sources:
            if expression.startswith(source):
                parts = expression.split('.', 1)
                self.source = source
                self.path = parts[1].split()[0]
                self.remaining = (
                    expression
                    .replace(f'{source}.{self.path}', '')
                    .strip()
                    )
                return True
        return False
    
    def get_value(self) -> Any:
        """Get the value from state or obj following the path"""
        source = self.potential_sources[self.source]
        value = glom(source, self.path)
        return value