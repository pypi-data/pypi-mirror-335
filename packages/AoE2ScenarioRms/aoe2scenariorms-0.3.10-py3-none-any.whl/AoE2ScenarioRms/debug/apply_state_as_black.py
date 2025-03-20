from typing import TYPE_CHECKING

from AoE2ScenarioParser.datasets.terrains import TerrainId
from AoE2ScenarioParser.helper.helper import xy_to_i

from AoE2ScenarioRms.debug.apply_debug import ApplyDebug
from AoE2ScenarioRms.util import GridMap

if TYPE_CHECKING:
    from AoE2ScenarioRms import AoE2ScenarioRms


class ApplyStateAsBlack(ApplyDebug):
    """

    Change all terrain tiles that are <state> (in the gridmap) to ``TerrainId.BLACK``

    """

    def __init__(self, rms: 'AoE2ScenarioRms', grid_map: 'GridMap', as_layer: bool = False) -> None:
        super().__init__(rms)

        mm = rms.scenario.map_manager
        map_size = mm.map_size

        for y in range(map_size):
            for x in range(map_size):
                if self.tile_should_be_black(grid_map, x, y):
                    if as_layer:
                        mm.terrain[xy_to_i(x, y, map_size)].layer = TerrainId.BLACK
                    else:
                        mm.terrain[xy_to_i(x, y, map_size)].terrain_id = TerrainId.BLACK

    def tile_should_be_black(self, grid_map: 'GridMap', x: int, y: int) -> bool:
        raise NotImplementedError("The function 'tile_should_be_black' was not implemented for this class")


class ApplyBlockedAsBlack(ApplyStateAsBlack):
    """

    Change all terrain tiles that are blocked (in the gridmap) to ``TerrainId.BLACK``

    """

    def tile_should_be_black(self, grid_map: 'GridMap', x: int, y: int) -> bool:
        return grid_map.is_blocked(x, y)


class ApplyAvailableAsBlack(ApplyStateAsBlack):
    """

    Change all terrain tiles that are available (in the gridmap) to ``TerrainId.BLACK``

    """

    def tile_should_be_black(self, grid_map: 'GridMap', x: int, y: int) -> bool:
        return grid_map.is_available(x, y)
