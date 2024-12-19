from typing import Any, Optional, Dict
from .expression import Expression

class VariableParser:
    """Main parser class for handling variable parsing with conditions"""
    
    def __init__(self):
        self.variable_map: Dict[str, str] = {}  # For custom variable mapping
    
    def add_variable_map(self, source: str, target: str) -> None:
        """Add a custom variable mapping"""
        self.variable_map[source] = target
    
    def evaluate(self, expression_str: str, state: dict, obj: Optional[dict] = None) -> Any:
        """Evaluate an expression string and return the result"""
        # Create and evaluate the expression
        expression = Expression.from_string(expression_str)
        
        # If it's not a parse expression, return as is
        if isinstance(expression, str):
            return expression
        
        # Apply variable mapping if exists
        if self.variable_map:
            for data_obj in expression.data_objects:
                if data_obj.source in self.variable_map:
                    data_obj.source = self.variable_map[data_obj.source]
        
        return expression.evaluate(state, obj) 