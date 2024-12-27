
from typing import Any, Dict, List
from src.parsers import Expression, StateConnector
from uuid import uuid4

class SmartPromptVariable:
    """
    Main parser for handling prompt variables.

    Usage:
    - Add your map with data sources to the 'object_map' attribute before initialization.
    - For each variable create an instance using this variable as an argument.
    - Pass list of variables to .generate_dict() to get a dictionary that you can use as input with any LangChain Runnable.
    - Access .parsed to get value just for this variable.

    """
    
    def __init__(self, raw_var: str):
        self.raw_var = raw_var
        self.uuid = str(uuid4())
        self._parsed = Expression(self.raw_var)
        PromptWrapper.parsed_vars[self.uuid] = self._parsed

    @property
    def parsed(self):
        return self._parsed.evaluate()

    
class PromptWrapper:
    """
    Wrap LangChain prompts.

    - Pass a prompt as arguments
    - Access dict with arguments via .values
    - Access prompt via .prompt
    """
    parsed_vars: Dict[str, Expression] = {} #lookup table

    def __init__(self, prompt):
        self._prompt = prompt
        self._vars: List[str] = prompt.input_variables
        self._smart_vars: List[str] = [var for var in self._vars 
                                       if var.startswith("SELECT")]

        self.smart_vars: List[SmartPromptVariable] = [SmartPromptVariable(var) 
                                                      for var in self._smart_vars]
        self.uuids: List[str] = [var.uuid for var 
                                 in self.smart_vars]
    @property
    def prompt(self):
        self._prompt.input_variables = self._combine_vars()
        for smart_var in self.smart_vars:
            self._prompt.template = self._prompt.template.replace(smart_var.raw_var, smart_var.uuid)
        return self._prompt
    
    @prompt.setter
    def prompt(self, new_prompt):
        self._prompt = new_prompt
    
    @property
    def raw_values(self):
        return self.generate_dict(self.vars)
    
    @property
    def values(self):
        vars_as_dict = {}
        for var in self.uuids:
            vars_as_dict[var] = (PromptWrapper
                                 .parsed_vars[var]
                                 .evaluate()
                                 )
        return vars_as_dict
    
    def _combine_vars(self):
        vars = []
        for var in self._vars:
            if var in self._smart_vars:
                continue
            else:
                vars.append(var)
        vars.extend(self.uuids)
        return vars
