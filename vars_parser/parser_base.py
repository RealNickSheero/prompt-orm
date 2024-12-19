from dataclasses import dataclass
from typing import Optional, Any

@dataclass
class ParseResult:
    """Result of parsing, containing the parsed object and remaining string"""
    obj: Any  # The parsed object
    remaining: str  # Remaining string to parse

class Parser:
    """Base class for all parsers"""
    @classmethod
    def try_parse(cls, expression: str) -> Optional[ParseResult]:
        """Try to parse the expression, return None if not applicable"""
        pass 