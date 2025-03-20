from __future__ import annotations

from enum import IntFlag, auto


class TerrainMark(IntFlag):
    """Flag used for marking specific object related aspects of the map"""

    NONE = auto()
    """Mark nothing"""
    WATER = auto()
    """Mark all water (excluding the shore line -> the first line of water next to the beach)"""
    BEACH = auto()
    """Mark all beach tiles"""
    SHORE = auto()
    """Mark the shore line -> the first line of water next to the beach"""
    LAND = auto()
    """Mark everything that is not water, shore or beach tiles."""

    WATER_SHORE_BEACH = WATER | SHORE | BEACH
    """Mark the water, shore and beach tiles"""
    ALL = WATER_SHORE_BEACH | LAND
    """
    Mark everything...... Nice and pointless... Why would you need this? 11
    
    Are you sure you don't need the opposite ``GridMapFactory`` function? Give the opposite a try:
     
    - ``GridMapFactory.block(...)`` or
    - ``GridMapFactory.select(...)``
    """
