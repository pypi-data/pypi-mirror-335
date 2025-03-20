from enum import Enum, auto


class GroupingMethod(Enum):
    """Enum to differentiate all possible ways groups can be arranged"""
    TIGHT = auto()
    """Tight grouping means all objects are aligned against each-other (not including diagonal)"""
    LOOSE = auto()
    """Loose grouping means objects are in the vicinity of each-other but not necessarily directly aligned"""
