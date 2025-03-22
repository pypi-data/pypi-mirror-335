"""Basic wrapper objects. Helps ease interopability across code base."""

from typing import Any
from enum import Enum, auto
from dataclasses import dataclass


class StateType(Enum):
    """MVP. need to evaluate which onese to add/remove"""
    TENSOR = auto()
    ARRAY = auto()
    STRING = auto()
    PRESENTABLE_RECORD = auto()
    PRESENTABLE_GROUP = auto()
    DICT = auto()
    OTHER = auto()


class ActionType(Enum):
    """MVP. need to evaluate which onese to add/remove"""
    INT = auto()
    STRING = auto()
    TENSOR = auto()
    ARRAY = auto()
    OTHER = auto()


@dataclass
class State:
    """A state object"""
    state_type: StateType         # The type of the state
    value: Any              # The value of the state
    label: Any = None       # A label for the state if one exists


@dataclass
class Action:
    """An action object"""
    value: Any              # The value of the action
    action_type: ActionType        # The type of the action
