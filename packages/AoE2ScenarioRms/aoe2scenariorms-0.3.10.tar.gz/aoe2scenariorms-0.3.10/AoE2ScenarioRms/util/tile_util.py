from __future__ import annotations

import random
from typing import Tuple, List

from AoE2ScenarioParser.objects.support.area import Area
from AoE2ScenarioParser.objects.support.tile import Tile


class TileUtil:
    _relative_adjacent = [(0, -1), (-1, 0), (1, 0), (0, 1)]

    @staticmethod
    def adjacent(x: int | Tile, y: int | None = None) -> List[Tile]:
        """Return all tiles adjacent to the given coordinate. (non-diagonal)"""
        tx, ty = TileUtil.coords(x, y)
        return [Tile(tx + x, ty + y) for x, y in TileUtil._relative_adjacent]

    @staticmethod
    def within_range(x: int | Tile, y: int | None = None, range_: int = 1, shuffle: bool = False) -> List[Tile]:
        """
        Return all tiles around this tile within a certain range. Range 1 would return a list of 9 tiles.
        A 3x3 converted to tiles with the given coordinate as center.

        Args:
            x: The x coordinate or the Tile itself
            y: The y coordinate or None (empty) if tile is given for x
            range_: The range around the tile to include
            shuffle: If the list should be shuffled

        Returns:
            A list of tiles that are within range of the given tile
        """
        x, y = TileUtil.coords(x, y)
        # Todo: Change this once Parser v1.0.0 comes around ;)
        tiles = Area(map_size=1000, x1=x, y1=y) \
            .expand(range_) \
            .to_coords()
        tiles.remove(Tile(x, y))

        tiles = list(tiles)

        if shuffle:
            random.shuffle(tiles)
        return tiles

    @staticmethod
    def coords(x: int | Tile, y: int | None = None) -> Tuple[int, int]:
        """Get the coords of a tile or xy params to make them consistent in functions."""
        if isinstance(x, Tile):
            return x
        return x, y

    @staticmethod
    def shuffled(tiles: List[Tile]) -> List[Tile]:
        # Todo: Add docstrings & tests
        copy_ = tiles.copy()
        random.shuffle(copy_)
        return copy_
