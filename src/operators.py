from abc import ABC, abstractmethod
from typing import Any, TypeVar, Generic, Dict, Type

T = TypeVar('T')

class BaseOperator(ABC, Generic[T]):
    """Base class for all operators"""
    symbol: str
    registry: Dict[str, Type['BaseOperator']] = {}
    SYMBOLS: Dict[str, callable] = {}
    
    def __init_subclass__(cls) -> None:
        """Register operator subclasses"""
        super().__init_subclass__()
        if hasattr(cls, 'SYMBOLS'):
            for symbol in cls.SYMBOLS:
                cls.registry[symbol] = cls
    
    def __init__(self, expression: str = None, left_idx: int = None):
        self.expression = expression
        self.symbol = None
        self.function: callable = None
        self.left = left_idx
        self.right = None
        self.remaining: str = None
        if expression is not None:
            self.parsed: bool = self.parse()
    
    def parse(self):
        expression = self.expression.strip()
        for symbol in self.SYMBOLS:
            if expression.startswith(symbol):
                self.symbol = symbol
                self.right = self.left + 1
                self.function = self.SYMBOLS[symbol]
                self.remaining = (
                    expression
                    .replace(f'{symbol}', '', 1)
                    .strip()
                    )
                return True
        return False
    
    def evaluate(self, left: T, right: T) -> Any:
        """Evaluate the operation between left and right operands"""
        return self.function(left, right)

class ConditionOperator(BaseOperator):
    """Operators for conditions (==, >, <, etc.)"""
    SYMBOLS = {
        '==': lambda x, y: x == y if not isinstance(y, bool) else x and y, 
        '!=': lambda x, y: x != y if not isinstance(y, bool) else x and y,
        '>': lambda x, y: x > y if isinstance(x, type(y)) or isinstance(y, type(x)) else False,
        '<': lambda x, y: x < y if isinstance(x, type(y)) or isinstance(y, type(x)) else False,
        '>=': lambda x, y: x >= y if isinstance(x, type(y)) or isinstance(y, type(x)) else False,
        '<=': lambda x, y: x <= y if isinstance(x, type(y)) or isinstance(y, type(x)) else False,
        'CONTAINS': lambda x, y: str(y).lower() in str(x).lower() if isinstance(x, (str, list)) else False,
        'NOT_CONTAINS': lambda x, y: str(y).lower() not in str(x).lower() if isinstance(x, (str, list)) else False,
    }
    
    def __init__(self, symbol):
        super().__init__()
        self.symbol = symbol
        self.function: callable = self.SYMBOLS[symbol]

class ExpressionOperator(BaseOperator):
    """Operators for combining conditions (AND, OR)"""
    SYMBOLS = {
        'AND': lambda x, y: [a and b for a, b in zip(x, y)] if isinstance(x, list) else x and y,
        'OR': lambda x, y: [a or b for a, b in zip(x, y)] if isinstance(x, list) else x or y,
    }

class ObjectOperator(BaseOperator):
    """Operators for combining data objects (+, -, etc.)"""
    SYMBOLS = {
        '+': lambda x, y: x + y if isinstance(x, (int, float, list)) else f"{x} {y}",
        '-': lambda x, y: x - y,
        '*': lambda x, y: x * y,
        '/': lambda x, y: x / y,
    }