from __future__ import annotations

from typing import List, Dict, Set

from AoE2ScenarioParser.datasets.players import PlayerId
from AoE2ScenarioParser.datasets.terrains import TerrainId
from AoE2ScenarioParser.objects.support.area import Area
from AoE2ScenarioParser.objects.support.tile import Tile
from AoE2ScenarioParser.scenarios.aoe2_de_scenario import AoE2DEScenario

from AoE2ScenarioRms.enums import TileLevel
from AoE2ScenarioRms.flags import TerrainMark, ObjectMark
from AoE2ScenarioRms.util.data import Data
from AoE2ScenarioRms.util.grid_map import GridMap
from AoE2ScenarioRms.util.tile_util import TileUtil
from AoE2ScenarioRms.util.unit_util import UnitUtil


class GridMapFactory:
    @staticmethod
    def select(
            scenario: 'AoE2DEScenario',
            terrain_marks: TerrainMark = None,
            object_marks: ObjectMark = None,
            terrain_ids: List[TerrainId] = None,
            object_consts: Dict[int, int] = None,
            area: Area = None
    ) -> GridMap:
        return GridMapFactory.mark(
            scenario=scenario,
            block_marked_tiles=False,
            terrain_marks=terrain_marks,
            object_marks=object_marks,
            terrain_ids=terrain_ids,
            object_consts=object_consts,
            area=area,
        )

    @staticmethod
    def block(
            scenario: 'AoE2DEScenario',
            terrain_marks: TerrainMark = None,
            object_marks: ObjectMark = None,
            terrain_ids: List[TerrainId] = None,
            object_consts: Dict[int, int] = None,
            area: Area = None
    ) -> GridMap:
        return GridMapFactory.mark(
            scenario=scenario,
            block_marked_tiles=True,
            terrain_marks=terrain_marks,
            object_marks=object_marks,
            terrain_ids=terrain_ids,
            object_consts=object_consts,
            area=area,
        )

    @staticmethod
    def mark(
            scenario: 'AoE2DEScenario',
            block_marked_tiles: bool,
            terrain_marks: TerrainMark = None,
            object_marks: ObjectMark = None,
            terrain_ids: List[TerrainId] = None,
            object_consts: Dict[int, int] = None,
            area: Area = None
    ) -> GridMap:
        starting_state = TileLevel.NONE if block_marked_tiles else TileLevel.TERRAIN
        set_marked_state = TileLevel.TERRAIN if block_marked_tiles else TileLevel.NONE

        mm, um = scenario.map_manager, scenario.unit_manager
        grid_map = GridMap(mm.map_size, starting_state)

        terrain_marks = terrain_marks if terrain_marks is not None else TerrainMark.NONE
        object_marks = object_marks if object_marks is not None else ObjectMark.NONE
        terrain_ids = terrain_ids if terrain_ids is not None else []
        object_consts = object_consts if object_consts is not None else {}

        # Mark all selected terrains
        terrain_ids = Data.get_terrain_ids_by_terrain_marks(terrain_marks) + terrain_ids
        marked_tiles: Set[Tile] = set()
        if len(terrain_ids):
            for t in mm.terrain:
                if t.terrain_id in terrain_ids:
                    marked_tiles.add(Tile(*t.xy))

        # Mark all tiles selected by an area
        if isinstance(area, Area):
            marked_tiles.update(area.to_coords())

        # Mark all shores
        requested_water_but_not_shore = TerrainMark.WATER in terrain_marks and TerrainMark.SHORE not in terrain_marks
        if TerrainMark.SHORE in terrain_marks or requested_water_but_not_shore:
            shore_tiles = set()
            beach_terrains = TerrainId.beach_terrains()
            water_terrains = TerrainId.water_terrains()
            for terrain_tile in mm.terrain:
                if terrain_tile.terrain_id in beach_terrains:
                    for tile in TileUtil.adjacent(*terrain_tile.xy):
                        if mm.get_tile(tile.x, tile.y).terrain_id in water_terrains:
                            shore_tiles.add(tile)

            if requested_water_but_not_shore:
                marked_tiles = marked_tiles.difference(shore_tiles)
            else:
                marked_tiles.update(shore_tiles)

        # Mark everything around trees and cliffs and optionally given consts
        trees, cliffs = Data.trees(), Data.cliffs()

        mark_trees = ObjectMark.TREES in object_marks
        mark_cliffs = ObjectMark.CLIFFS in object_marks
        for obj in um.units[PlayerId.GAIA]:
            if mark_trees and obj.unit_const in trees:
                marked_tiles.update(UnitUtil.get_tiles_around_object(obj, 1))
            elif mark_cliffs and obj.unit_const in cliffs:
                marked_tiles.update(UnitUtil.get_tiles_around_object(obj, 2))

        units = um.filter_units_by_const(list(object_consts.keys()))
        for unit in units:
            marked_tiles.update(UnitUtil.get_tiles_around_object(unit, object_consts[unit.unit_const]))

        for tile in marked_tiles:
            grid_map.set(set_marked_state, tile)
        return grid_map
