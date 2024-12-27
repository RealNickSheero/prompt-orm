from typing import Any, Optional, Dict, List
import re
from glom import glom, flatten #type: ignore
from typeguard import check_type, CollectionCheckStrategy, TypeCheckError #type: ignore
from src.operators import ExpressionOperator, ObjectOperator, ConditionOperator, ExpressionOperator
from src.field import ConditionArgument, ConditionMask
from abc import ABC, abstractmethod
from dataclasses import dataclass

class StateConnector:
    """
    Contains available data sources.

    Requires a dict:
    {source_name: source}
    """
    object_map: dict = {}

    def __init__(self, object_map):
        StateConnector.object_map = object_map
        

class Expression:
    """
    Extract and evaluate all conditions and data objects.
    """
    def __init__(self, expression_str: str):
        self.original_expression: str = expression_str
        self.processed_query: dict = self._split_expression(expression_str)

        self.sources: List[Source] = []
        self.conditions: List[Condition] = []
        self.fields: List[Field] = []
        
        self.object_operators: Optional[List[ObjectOperator]] = []
        self.expression_operators: List[ExpressionOperator] = []
        self._parse_components("select",
                               Field, 
                               self.fields
                               )
        self._parse_components("from",
                               Source, 
                               self.sources
                               )
        self._parse_components("where",
                               Condition,
                               self.conditions, 
                               ExpressionOperator,
                               self.expression_operators,
                               )
        
    def evaluate(self) -> Any:
        """
        Evaluate the complete expression
        """
        evaluated_objects = [source.evaluate() for source in self.sources]
        evaluated_objects = next(iter(evaluated_objects)) # In case if I want to add JOINs
        
        if self.conditions:
            bool_mask = self._generate_conditions_mask(evaluated_objects)
            evaluated_objects = [value for value, mask 
                                 in zip(evaluated_objects, bool_mask) 
                                 if mask]
        if "*" in self.fields:
            return evaluated_objects
        
        d = {field.evaluate():field.evaluate() for field in self.fields}
        filtered_data = [glom(obj, d) for obj in evaluated_objects]
        return filtered_data

    def _parse_components(self, 
                          query_key,
                          component_class, 
                          components_list,
                          operator_class = None, 
                          operators_list = None):
        """Generic method to parse components and their operators
        
        Args:
            component_class: Class to parse (DataObject or Condition)
            operator_class: Operator class to use (ObjectOperator or ExpressionOperator)
            components_list: List to store parsed components
            operators_list: List to store parsed operators
        """
        raw_components = self.processed_query[query_key]
        for i, raw_component in enumerate(raw_components):
                component = component_class(raw_component)
                if component.parsed:
                    component.idx = (1 + components_list[-1].idx 
                                    if components_list else 0)
                    components_list.append(component)
                    raw_components[i] = component.remaining
                    if raw_components[i] and operator_class:
                        operator = operator_class(raw_components[i], component.idx)
                        if operator.parsed:
                            operators_list.append(operator)
                            self.processed_query[query_key][i] = operator.remaining
                            self._parse_components(query_key,
                                                component_class, 
                                                components_list,
                                                operator_class, 
                                                operators_list,
                                                )
    
    def _split_expression(self, expression): 
        query_patterns = {"select": r"SELECT\s+(.*?)\s+FROM",
                          "from": r"FROM\s+(.*?)(?:\s+WHERE|$)",
                          "where": r"WHERE\s+(.+)$"}
        for key, pattern in query_patterns.items():
            match = re.search(pattern, expression)
            if match:
                query_components = match.group(1)
                query_components = [component.strip() for component in query_components.split(',')]
                query_patterns[key] = query_components
            else:
                query_patterns[key] = ""
        return query_patterns

    
    def _generate_conditions_mask(self, evaluated_objects: List[Any]):
        condition_masks = {} 
        for condition in self.conditions: # create bool masks for each condition
            condition_masks[condition.idx] = (condition.evaluate(source=evaluated_objects,
                                                                source_name="name_placeholder")
                                                       .mask)

        if self.expression_operators: #if more than one condition 
            for operator in self.expression_operators: # use operator to iterate over each condition mask to create one mask 
                    condition_masks[operator.right] = operator.evaluate(
                                                                condition_masks[operator.left], 
                                                                condition_masks[operator.right]
                                                                )
                    condition_masks.pop(operator.left)

        return next(iter(condition_masks.values()))
    
class BaseParser(ABC):
    def __init__(self, expression: str):
        self.expression = expression
        self.remaining: str = None
        self.idx: int = 0
        self.parsed: bool = self.parse()

    @abstractmethod
    def parse(self) -> bool:
        pass
    
class Field(BaseParser):

    def __init__(self, expression):
        self.path_parts: List[str] = None
        super().__init__(expression)

    def evaluate(self):
        return ".".join(self.path_parts)

    def parse(self) -> bool:
        expression = self.expression.strip()
        parts = expression.split('.')
        self.path_parts = parts
        return True

class Source(BaseParser):
    """
    Extract and store data from provided variable. 
    """
    def __init__(self, expression: str):
        self.source: str = None
        self.path: str = None
        super().__init__(expression)
    
    def parse(self) -> bool:
        expression = self.expression.strip()
        for source in StateConnector.object_map:
            if expression.startswith(source):
                self.source, _, self.path = expression.partition('.')
                for op in ObjectOperator.SYMBOLS:
                    if self.path and f' {op} ' in self.path:
                        path, _, remaining = self.path.partition(f' {op} ')
                        self.path = path.strip()
                        self.remaining = f'{op} {remaining}'.strip()
                        break
                else:
                    self.remaining = ""
                    return True
        return False
    
    def evaluate(self) -> List[Any]:
        source = StateConnector.object_map[self.source]
        if not self.path:
            return source
        extracted = glom(source, self.path)
        try:
            check_type(extracted, 
                       List[list], 
                       collection_check_strategy=CollectionCheckStrategy.ALL_ITEMS)
            flat_list = flatten(extracted)
            return flat_list
        except TypeCheckError:
            if isinstance(extracted, list):
                return extracted
            else:
                return [extracted]

class Condition(BaseParser):
    """
    Extract and store conditions from provided variable.
    """
    def __init__(self, expression: str):
        self.attribute: ConditionArgument = None
        self.operator: ConditionOperator = None 
        self.value: ConditionArgument = None
        super().__init__(expression)

    def parse(self) -> bool:
        expression = self.expression.strip()
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
                self.attribute = ConditionArgument(attribute.strip())
                self.operator = ConditionOperator(op)
                self.value = ConditionArgument(value.strip())
                return True
        return False

    def evaluate(self, source: List[Any], source_name: str) -> ConditionMask:
        mask = []
        for obj in source:
            args = {'left': self.attribute, 
                    'right': self.value}
            for position, argument in args.items():
                if argument.object:
                    path = argument.processed
                    extracted = glom(obj, path)
                    args[position] = argument._convert_string(extracted)
                else:
                    args[position] = argument._convert_string(argument.processed)
            result = (self
                    .operator
                    .function(args['left'], 
                              args['right']
                            ))
            mask.append(result)
        
        return ConditionMask(mask=mask, 
                             source_name=source_name)