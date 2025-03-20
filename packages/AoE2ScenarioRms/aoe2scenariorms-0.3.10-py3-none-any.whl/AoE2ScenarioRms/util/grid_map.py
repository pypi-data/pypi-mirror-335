from __future__ import annotations

import random
from typing import List

from AoE2ScenarioParser.objects.support.area import Area
from AoE2ScenarioParser.objects.support.tile import Tile

from AoE2ScenarioRms.enums import TileLevel
from AoE2ScenarioRms.util.tile_util import TileUtil


class GridMap:
    def __init__(self, map_size: int, starting_state: TileLevel = TileLevel.NONE) -> None:
        """
        Class that manages the state of a map. Used for marking tiles on a scenario for creation of potential group
        spawns.

        Args:
            map_size: The size of the map to manage
            starting_state: The starting state of all tiles
        """
        self.map_size: int = map_size
        self.grid_map: List[List[TileLevel]] = []

        self.set_all(starting_state)

    def available_tiles(self, size=1, shuffle=False) -> List[Tile]:
        """
        Get all tiles available for resource spawning. Can be shuffled if necessary

        Args:
            size: The size of the object
            shuffle: If the resulting array should be returned shuffled or not

        Returns:
            A (shuffled) list of ``Tile`` objects that indicate which tiles are valid for spawn attempts for groups
        """
        tiles = []
        for y in range(self.map_size):
            for x in range(self.map_size):
                if self.is_available_size(size, x, y):
                    tiles.append(Tile(x, y))
        if shuffle:
            random.shuffle(tiles)
        return tiles

    def is_available_size(self, size: int, x: int | Tile, y: int = None) -> bool:
        """Check if a tile and tiles around it are available within a given size"""
        x, y = TileUtil.coords(x, y)
        if size == 1:
            return self.is_available(x, y)

        area = Area(map_size=self.map_size, x1=x, y1=y).size(size)
        # If the area selection went below zero the 'area' gets cut off. This verifies that that didn't happen
        if area.get_width() != size or area.get_height() != size:
            return False

        for tile in area.to_coords():
            if self.is_blocked(tile):
                return False
        return True

    def invert(self) -> GridMap:
        """
        Invert the gridmap inline

        Returns:
            The current instance, so this it can be chained if necessary
        """
        for y in range(self.map_size):
            for x in range(self.map_size):
                if self.is_available(x, y):
                    self.set(TileLevel.TERRAIN, x, y)
                else:
                    self.set(TileLevel.NONE, x, y)
        return self

    def set(self, level: TileLevel, x: int | Tile, y: int = None) -> None:
        """Set a coordinate to a specific level"""
        x, y = TileUtil.coords(x, y)
        self.grid_map[y][x] = level

    def temp(self, x: int | Tile, y: int = None) -> None:
        """Set a coordinate to the ``TEMP`` TileLevel"""
        self.set(TileLevel.TEMP, x, y)

    def reset(self, x: int | Tile, y: int = None) -> None:
        """Set a coordinate to the ``NONE`` TileLevel"""
        self.set(TileLevel.NONE, x, y)

    def set_all(self, state: TileLevel) -> None:
        """Set all coordinates to a specific level"""
        self.grid_map = [[state for _ in range(self.map_size)] for _ in range(self.map_size)]

    def is_available(self, x: int | Tile, y: int = None) -> bool:
        """If a given tile is available for group spawning"""
        x, y = TileUtil.coords(x, y)
        return self.grid_map[y][x] == TileLevel.NONE

    def is_blocked(self, x: int | Tile, y: int = None) -> bool:
        """Inverse of ``is_available(...)``. If a given tile is NOT available for group spawning"""
        return not self.is_available(x, y)

    def level_is_available(self, level: TileLevel, x: int | Tile, y: int = None) -> bool:
        """If a given tile is available based on the given level"""
        x, y = TileUtil.coords(x, y)
        if self.grid_map[y][x] == TileLevel.TEMP:
            return True
        if level > self.grid_map[y][x]:
            return True
        return False

    def level_is_blocked(self, level: TileLevel, x: int | Tile, y: int = None) -> bool:
        """Inverse of ``level_is_available(...)``. If a given tile is NOT available based on the given level"""
        return not self.level_is_available(level, x, y)

    def is_valid(self, level: TileLevel, x: int | Tile, y: int = None) -> bool:
        """If a given tile is a valid (not outside the map) and available based on the given level"""
        x, y = TileUtil.coords(x, y)
        is_within_map = 0 <= x <= self.map_size - 1 and 0 <= y <= self.map_size - 1
        return is_within_map and self.level_is_available(level, x, y)
