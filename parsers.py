from typing import Any, Optional, Dict, List
from glom import glom #type: ignore
from operators import ExpressionOperator, ObjectOperator, ConditionOperator, ExpressionOperator
from field import Value, Attribute

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
        print(f"Parsing conditions from remaining: '{self.remaining}'")
        condition = Condition(self.remaining)
        if condition.parsed:
            condition.idx = (1 + self.conditions[-1].idx 
                             if self.conditions else 0)
            self.conditions.append(condition)
            print(f"Added condition with idx {condition.idx}")
            self.remaining = condition.remaining
            if condition.remaining:
                operator = ExpressionOperator(self.remaining, condition.idx)
                if operator.parsed:
                    self.expression_operators.append(operator)
                    print(f"Added expression operator: {operator.symbol}")
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
    
        values = next(iter(values.values()), None).value
        if values is None:
            return None
        if self.conditions:
            print(f"Evaluating conditions on values: {values}")
            if not isinstance(values, list):
                values = [values]

            condition_masks = {} # create bool masks for each condition
            for condition in self.conditions:
                condition_masks[condition.idx] = list(map(condition.evaluate, values))
                print(f"Condition {condition.idx} masks: {condition_masks[condition.idx]}")

            if self.expression_operators:
                print(f"Processing expression operators: {[op.symbol for op in self.expression_operators]}")
                for operator in self.expression_operators: # use operator to iterate over masks to create one mask 
                        left = condition_masks[operator.left]
                        right = condition_masks[operator.right]
                        mask = operator.evaluate(left, right)
                        print(f"Operator {operator.symbol}: {left} {operator.symbol} {right} = {mask}")
                        condition_masks[operator.right] = mask
                        condition_masks.pop(operator.left)

            masks = next(iter(condition_masks.values()))
            print(f"Final masks: {masks}")
            values = [value for value, mask in zip(values, masks) if mask]
            print(f"Filtered values: {values}")

        return values
    

class SmartPromptVariable:
    """Main parser class for handling variable parsing with conditions"""

    parsed_vars: Dict[str, Expression] = {}
    object_map = {}
    
    def __init__(self, raw_var: str):
        if not self.object_map:
            raise ValueError("Object map is empty. Setup object map first.")
        
        self.raw_var = raw_var
        self._parsed = Expression(self.raw_var)
        self.parsed_vars[raw_var] = self._parsed

    @property
    def parsed(self):
        return self._parsed.evaluate()
    
    @classmethod
    def generate_dict(cls, prompt_vars: List[str]) -> Dict[str, Any]:
        vars_as_dict = {}
        for var in prompt_vars:
            if var in cls.parsed_vars.keys():
                vars_as_dict[var] = cls.parsed_vars[var].evaluate()
        return vars_as_dict


class DataObject:
    """Represents a data object"""
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
        for source in SmartPromptVariable.object_map:
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
        source = SmartPromptVariable.object_map[self.source]
        print(source)
        value = glom(source, self.path)
        return value

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
        expression = self.expression.strip().removeprefix('WHERE ').strip()
        for op in ConditionOperator.SYMBOLS:
            if f' {op} ' in expression:
                attribute, _, raw_value = expression.partition(f' {op} ')
                for log_op in ExpressionOperator.SYMBOLS:
                    if f' {log_op} ' in raw_value:
                        value, _, remaining = raw_value.partition(f' {log_op} ')
                        self.remaining = f'{log_op} {remaining}'.strip()
                        break
                else:
                    value, self.remaining = raw_value, ''
                self.attribute = Attribute(attribute.strip())
                self.operator = ConditionOperator(op)
                self.value = Value(value.strip())
                return True
        return False

    def evaluate(self, obj: Any) -> bool:
        print(f"Evaluating condition on object: {obj}")
        if isinstance(obj, dict):
            left = obj.get(self.attribute.name)
        else:
            left = getattr(obj, self.attribute.name)
        left = Value(left).processed
        right = self.value.processed
        print("LEFT", left)
        print("RIGHT", right)
        print(f"Comparing {left} {self.operator.symbol} {right}")
        result = self.operator.function(left, right)
        print(f"Result: {result}")
        return result