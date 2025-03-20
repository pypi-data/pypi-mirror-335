from __future__ import annotations

from enum import IntEnum


class TileLevel(IntEnum):
    """
    Enum to differentiate between different levels a tile can be 'marked' for.
    Necessity of this enum is arguable right now. Might be removed in the future.
    """
    NONE = 0
    RES = 30
    TERRAIN = 50
    TEMP = 9998
    ALL = 9999
