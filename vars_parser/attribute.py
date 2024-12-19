from typing import Any, Dict
from dataclasses import dataclass

class Attribute:
    """Represents a field in a data object"""
    def __init__(self, name: str): 
        self.name: str = name.strip()