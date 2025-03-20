import math

from AoE2ScenarioParser.objects.data_objects.unit import Unit
from AoE2ScenarioParser.objects.support.tile import Tile
from AoE2ScenarioParser.scenarios.scenario_store import actions
from ordered_set import OrderedSet


class UnitUtil:
    @staticmethod
    def get_tiles_around_object(unit: Unit, range_: int) -> OrderedSet[Tile]:
        """Get tiles around an object within a given range"""
        # Todo: change this function to use TileUtil....
        area = actions.new_area_object(unit._uuid)
        # Range around a unit on both sides including the center tile (hence the + 1)
        radius = range_ * 2 + 1
        return area.select_centered(math.floor(unit.x), math.floor(unit.y), radius, radius).to_coords()
