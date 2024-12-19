from typing import Any, Dict, List, Optional
from .condition import Condition
from .data_object import DataObject
from .operators import ExpressionOperator, ObjectOperator

class Expression:
    """Represents a complete expression with data objects and conditions"""
    def __init__(self, expression_str: str):
        self.original_expression = expression_str
        self.data_objects: List[DataObject] = []
        self.conditions: List[Condition] = []
        self.object_operators: Optional[Any] = []
        self.expression_operators: List[ExpressionOperator] = []
        self.remaining = expression_str
        self._parse_dataobjects()
        self._parse_conditions()

    def _parse_dataobjects(self):
        """Parse data objects from the expression"""
        data_object = DataObject(self.remaining)
        if data_object.parsed:
            data_object.idx = (1 + self.data_objects[-1].idx 
                               if self.data_objects else 0)
            self.data_objects.append(data_object)
            self.remaining = data_object.remaining
            if data_object.remaining:
                operator = ObjectOperator(self.remaining, data_object.idx)
                if operator.parsed:
                    self.object_operators.append(operator)
                    self.remaining = operator.remaining
                    self._parse_dataobjects()
        pass

    def _parse_conditions(self):
        """Parse conditions from the expression"""
        condition = Condition(self.remaining)
        if condition.parsed:
            condition.idx = (1 + self.conditions[-1].idx 
                             if self.conditions else 0)
            self.conditions.append(condition)
            self.remaining = condition.remaining
            if condition.remaining:
                operator = ExpressionOperator(self.remaining, condition.idx)
                if operator.parsed:
                    self.expression_operators.append(operator)
                    self.remaining = operator.remaining
                    self._parse_conditions()
        pass

    def evaluate(self) -> Any:
        """Evaluate the complete expression"""
        # Evaluate data objects
        values = {obj.idx:obj for obj in self.data_objects}
        if self.object_operators and len(values.keys()) > 1:
            for operator in self.object_operators:
                left = values[operator.left]
                right = values[operator.right]
                value = operator.evaluate(left.value, right.value)
                right.value = value
                values.pop(left.idx)
    
        values = next(iter(values.values()), None)
        if values is None:
            return None

        if self.conditions:
            if not isinstance(values, list):
                values = [values]

            condition_masks = {} # create bool masks for each condition
            for condition in self.conditions:
                condition_masks[condition.idx] = list(map(condition.evaluate, values))

            if self.expression_operators:
                for operator in self.expression_operators: # use operator to iterate over masks to create one mask 
                        left = condition_masks[operator.left]
                        right = condition_masks[operator.right]
                        mask = operator.evaluate(left, right)
                        condition_masks[operator.right] = mask
                        condition_masks.pop(operator.left)

            masks = next(iter(condition_masks.values()))
            values = [value for value, mask in zip(values, masks) if mask]            

        return values