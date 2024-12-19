from abc import ABC, abstractmethod
from typing import Any, TypeVar, Generic, Dict, Type
from datetime import datetime

T = TypeVar('T')

class BaseOperator(ABC, Generic[T]):
    """Base class for all operators"""
    symbol: str
    registry: Dict[str, Type['BaseOperator']] = {}
    
    def __init_subclass__(cls) -> None:
        """Register operator subclasses"""
        super().__init_subclass__()
        if hasattr(cls, 'SYMBOLS'):
            for symbol in cls.SYMBOLS:
                cls.registry[symbol] = cls
    
    @abstractmethod
    def evaluate(self, left: T, right: T) -> Any:
        """Evaluate the operation between left and right operands"""
        pass
    
    @classmethod
    def get_operator(cls, symbol: str) -> 'BaseOperator':
        """Get operator instance by symbol"""
        if symbol not in cls.registry:
            raise ValueError(f"Unknown operator: {symbol}")
        return cls.registry[symbol](symbol)

class ConditionOperator(BaseOperator):
    """Operators for conditions (==, >, <, etc.)"""
    SYMBOLS = {
        '==': lambda x, y: x == y,
        '!=': lambda x, y: x != y,
        '>': lambda x, y: x > y if isinstance(x, type(y)) or isinstance(y, type(x)) else False,
        '<': lambda x, y: x < y if isinstance(x, type(y)) or isinstance(y, type(x)) else False,
        '>=': lambda x, y: x >= y if isinstance(x, type(y)) or isinstance(y, type(x)) else False,
        '<=': lambda x, y: x <= y if isinstance(x, type(y)) or isinstance(y, type(x)) else False,
        'CONTAINS': lambda x, y: str(y).lower() in str(x).lower() if isinstance(x, (str, list)) else False,
        'NOT_CONTAINS': lambda x, y: str(y).lower() not in str(x).lower() if isinstance(x, (str, list)) else False,
    }
    
    def __init__(self, symbol):
        self.symbol = symbol
        self.function: callable = self.SYMBOLS[symbol]
    
    def evaluate(self, left, right):
        return self.function(left, right)

class ExpressionOperator(BaseOperator):
    """Operators for combining conditions (AND, OR)"""
    SYMBOLS = {
        'AND': lambda x, y: x and y,
        'OR': lambda x, y: x or y,
    }
    
    def __init__(self, expression: str, left_idx: int):
        self.expression = expression
        self.symbol = None
        self.function: callable = None
        self.left = left_idx
        self.right = None
        self.remaining: str = None
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
                    .replace(f'{symbol}', '')
                    .strip()
                    )
                return True
        return False
    
    def evaluate(self, left, right):
        return self.function(left, right)

class ObjectOperator(BaseOperator):
    """Operators for combining data objects (+, -, etc.)"""
    SYMBOLS = {
        '+': lambda x, y: x + y if isinstance(x, (int, float)) else f"{x} {y}",
        '-': lambda x, y: x - y,
        '*': lambda x, y: x * y,
        '/': lambda x, y: x / y,
    }

    def __init__(self, expression: str, left_idx: int):
        self.expression = expression
        self.symbol = None
        self.function = None
        self.left = left_idx
        self.right = None
        self.remaining: str = None
        self.parsed: bool = self.parse()

    def parse(self):
        expression = self.expression.strip()
        for symbol in self.SYMBOLS:
            if expression.startswith(f"{symbol} "):
                self.symbol = symbol
                self.right = self.left + 1
                self.function = self.SYMBOLS[symbol]
                self.remaining = (
                    expression
                    .replace(f'{symbol}', '')
                    .strip()
                    )
                return True
        return False
    
    def evaluate(self, left, right):
        return self.function(left, right)