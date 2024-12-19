from typing import Any, Dict, Optional
from dataclasses import dataclass
from .attribute import Attribute
from .value import Value
from .operators import ConditionOperator
from .parser_base import ParseResult, Parser

class Condition:
    """Represents a single condition in a WHERE clause"""
    def __init__(self, expression):
        self.expression: str = expression
        self.attribute: Attribute = None
        self.operator: ConditionOperator = None 
        self.value: Value = None
        self.remaining: str = None
        self.parsed: bool = self.parse()
        self.idx = 0

    def parse(self) -> bool:
        """Parse a condition from the expression string"""
        expression = self.expression.strip()
        if expression.startswith('WHERE'):
            for op_str in ConditionOperator.SYMBOLS:
                if f' {op_str} ' in expression:
                    parts = expression.split(f' {op_str} ', 1)
                    if len(parts) == 2:
                        self.attribute = Attribute(parts[0].strip())
                        self.value = Value(parts[1].strip())
                        self.operator = ConditionOperator(op_str)
                        self.remaining = (
                            expression
                            .replace(f'{parts[0]} {op_str} {parts[1]}', '')
                            .strip()
                        )
                        return True
        return False

    def evaluate(self, obj: Any) -> bool:
        if isinstance(obj, dict):
            left = obj.get(self.attribute.name)
        else:
            left = getattr(obj, self.attribute.name)
        right = self.value.processed
        return self.operator.function(left, right)