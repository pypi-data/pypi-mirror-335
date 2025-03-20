from __future__ import annotations

import random
from typing import Tuple, List, TYPE_CHECKING

from AoE2ScenarioParser.helper.printers import warn
from AoE2ScenarioParser.objects.support.tile import Tile

from AoE2ScenarioRms.enums import GroupingMethod, TileLevel
from AoE2ScenarioRms.errors import SpawnFailureWarning
from AoE2ScenarioRms.util.tile_util import TileUtil

if TYPE_CHECKING:
    from AoE2ScenarioRms.rms import CreateObjectConfig
    from AoE2ScenarioRms.util.grid_map import GridMap


class Locator:
    """

    Utility class for locating tiles in a map based on the given criteria

    """

    @staticmethod
    def create_groups(config: 'CreateObjectConfig', grid_map: 'GridMap') -> List[List[Tile]]:
        """
        Create groups for the given create object config.

        Args:
            config: The config object to be used for the groups
            grid_map: The grid map to be taken into account when creating the groups

        Returns:
            A list of groups. Each group is also a list of tiles.
        """
        available_tiles = grid_map.available_tiles(size=config.object_size, shuffle=True)

        amount = config.max_potential_group_count
        name = config.name

        groups: List[List[Tile]] = []
        if amount * 2 > len(available_tiles):
            warn(f"For group '{name}', the amount of groups requested is really high. "
                 f"({amount} groups compared to {len(available_tiles)} available tiles).\n"
                 f"Consider lowering the max amount of necessary groups for '{name}'.", SpawnFailureWarning, 3)

        # starting_tiles = self.find_random_locations(amount)
        starting_tiles = available_tiles[:amount]

        failed_spawns = 0
        for starting_tile in starting_tiles:
            min_, size = Locator.randomize_group_size(config.number_of_objects)

            group = [starting_tile]
            size -= 1

            group, success = Locator.find_group_tiles(
                grid_map,
                config.grouping,
                size,
                group,
                loose_grouping_distance=config.loose_grouping_distance
            )

            if len(group) < min_:
                failed_spawns += 1
                continue
            groups.append(group)

        if failed_spawns and failed_spawns / amount > .1:
            warn(f"When generating group '{name}', out of the {amount} groups, {failed_spawns} failed. "
                 f"Consider lowering the max amount of necessary groups for '{name}'.", SpawnFailureWarning)

        return groups

    @staticmethod
    def find_group_tiles(
            grid_map: GridMap,
            method: GroupingMethod,
            amount: int,
            group: List[Tile],
            *,  # after this, kwarg only
            loose_grouping_distance: int = -1
    ) -> Tuple[List[Tile], bool]:
        """
        Find tiles as a group based on the method of searching given through ``method``.

        Args:
            grid_map: The gridmap to respect
            method: The method of searching of tiles to use
            amount: The amount of tiles to return
            group: The current ranged_tiles belonging to this group (to not return a tile twice)
            loose_grouping_distance: The range in which to search for tiles, only used with: ``GroupingMethod.LOOSE``

        Returns:
            A tuple containing a list of tiles and a boolean indicating if the amount of tiles in the list is equal to
            the amount requested
        """
        if method == GroupingMethod.TIGHT:
            return Locator.find_random_adjacent_tiles(grid_map, amount, group)
        elif method == GroupingMethod.LOOSE:
            return Locator.find_random_tiles_within_range(grid_map, amount, group, loose_grouping_distance)
        return [], False

    @staticmethod
    def find_random_adjacent_tiles(
            grid_map: GridMap,
            amount: int,
            group: List[Tile]
    ) -> Tuple[List[Tile], bool]:
        """
        Find random adjacent tiles (not diagonal) around a given tile and tiles added to the group around the initial
        tile.

        Args:
            grid_map: The gridmap to respect
            amount: The maximum amount of tiles to return on top of the tiles from the given group,
            group: The current tiles belonging to this group (to not return a tile twice). Has to include at least one
                tile

        Returns:
            A tuple containing a list of tiles and a boolean indicating if the amount of tiles in the list is equal to
            the amount requested
        """
        if amount == 0:
            return group, True

        goal = amount + len(group)

        for _ in range(amount):
            for tile in TileUtil.shuffled(group):
                adjacent_tile = Locator._find_first_valid_in_list(grid_map, group, TileUtil.adjacent(tile))

                if adjacent_tile:
                    group.append(adjacent_tile)
                    if len(group) == goal:
                        return group, True
                    break

        return group, False

    @staticmethod
    def find_random_tiles_within_range(
            grid_map: GridMap,
            amount: int,
            group: List[Tile],
            range_: int
    ) -> Tuple[List[Tile], bool]:
        """
        Find random tiles within a given range around the center of the group

        Args:
            grid_map: The gridmap to respect
            amount: The amount of tiles to return
            range_: The range in which to search for ranged_tiles
            group: The current ranged_tiles belonging to this group (to not return a tile twice)

        Returns:
            A tuple containing a list of tiles and a boolean indicating if the amount of tiles in the list is equal to
            the amount requested
        """
        if amount == 0:
            return group, True

        ranged_tiles = TileUtil.within_range(group[0], range_=range_)
        tiles, success = Locator._find_valid_in_list(grid_map, group, ranged_tiles, amount)

        if success:
            return group + tiles, True

        return group, False

    @staticmethod
    def _find_first_valid_in_list(
            grid_map: GridMap,
            group: List[Tile],
            lst: List[Tile],
            *,
            shuffled: bool = True
    ) -> Tile | None:
        """
        Same as ``_find_valid_in_list`` but only requests one and returns that without the list.

        Args:
            grid_map: The gridmap to respect
            group: The current group (to avoid returning a tile twice)
            lst: The source list to get the tiles from
            shuffled: If the list should be shuffled before it's checked (meaning: random result)

        Returns:
            The first tile from the list or None if nothing was found
        """
        tiles, success = Locator._find_valid_in_list(grid_map, group, lst, 1, shuffled=shuffled)
        return tiles[0] if success else None

    @staticmethod
    def _find_valid_in_list(
            grid_map: GridMap,
            group: List[Tile],
            lst: List[Tile],
            amount: int = 1,
            *,
            shuffled: bool = True,
    ) -> Tuple[List[Tile], bool]:
        """
        Find random tiles within a given list

        Args:
            grid_map: The gridmap to respect
            group: The current group (to avoid returning a tile twice)
            lst: The source list to get the tiles from
            amount: The amount of tiles to return
            shuffled: If the list should be shuffled before it's checked (meaning: shuffled result)

        Returns:
            A tuple containing a list of tiles and a boolean indicating if the amount of tiles in the list is equal to
            the amount requested
        """
        tiles = []

        lst = TileUtil.shuffled(lst) if shuffled else lst
        for adjacent_tile in lst:
            if adjacent_tile not in group and grid_map.is_valid(TileLevel.RES, adjacent_tile):
                tiles.append(adjacent_tile)
                if len(tiles) == amount:
                    return tiles, True
        return [], False

    @staticmethod
    def randomize_group_size(size: int | Tuple[int, int]) -> Tuple[int, int]:
        """
        Args:
            size: The size of a group

        Returns:
            A tuple with the minimum valid size for a group as first value, and if the given size is a tuple the second
            value is a randomized value between the 2 numbers. If an int was given, the int is returned as second value.
        """
        if isinstance(size, tuple):
            return size[0], random.randint(size[0], size[1])
        else:
            return size, size
