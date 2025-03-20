from __future__ import annotations

from enum import IntFlag, auto


class ObjectMark(IntFlag):
    """Flag used for marking specific object related aspects of the map"""

    NONE = auto()
    """Mark nothing"""
    TREES = auto()
    """Mark around all trees"""
    CLIFFS = auto()
    """Mark around all cliffs"""

    ALL = TREES | CLIFFS
    """Mark trees and cliffs"""
