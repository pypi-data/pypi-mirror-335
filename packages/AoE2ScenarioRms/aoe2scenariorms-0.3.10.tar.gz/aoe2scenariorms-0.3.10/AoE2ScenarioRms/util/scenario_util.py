import math
from typing import List

from AoE2ScenarioParser.datasets.players import PlayerId
from AoE2ScenarioParser.datasets.terrains import TerrainId
from AoE2ScenarioParser.helper.helper import xy_to_i
from AoE2ScenarioParser.objects.data_objects.unit import Unit
from AoE2ScenarioParser.scenarios.aoe2_de_scenario import AoE2DEScenario

from AoE2ScenarioRms.flags import ObjectClear
from AoE2ScenarioRms.util.data import Data


class ScenarioUtil:
    @staticmethod
    def clear(
            scenario: AoE2DEScenario,
            clear: ObjectClear = None,
            consts: List[int] = None,
            units: List[Unit] = None
    ) -> None:
        """
        Clear objects from a scenario to make place for randomized objects

        Args:
            scenario: The scenario to clear objects from
            clear: The flag indicating what to clear and what to leave
            consts: A list of object consts to clear on top of the clear flag
            units: A list of unit objects to clear on top of the flag and consts
        """
        um, mm = scenario.unit_manager, scenario.map_manager

        if clear is None:
            clear = ObjectClear.RESOURCE_OBJECTS + ObjectClear.ANIMAL_OBJECTS

        consts = consts if consts is not None else []
        units = units if units is not None else []

        # Clear all player related objects
        if ObjectClear.PLAYERS in clear:
            for i in PlayerId.all(exclude_gaia=True):
                um.units[i] = []

        # Mark resources
        resource_consts = Data.get_object_consts_by_clear_options(clear)
        objects_to_remove = set(obj for obj in um.units[PlayerId.GAIA] if obj.unit_const in resource_consts)

        # Mark straggler trees
        if ObjectClear.STRAGGLERS in clear:
            tree_consts = Data.trees()
            for u in um.units[PlayerId.GAIA]:
                underlying_terrain = mm.terrain[xy_to_i(math.floor(u.x), math.floor(u.y), mm.map_size)].terrain_id
                if u.unit_const in tree_consts and underlying_terrain not in TerrainId.tree_terrains():
                    objects_to_remove.add(u)

        # Mark given consts
        if len(consts):
            objects_to_remove.update(set(um.filter_units_by_const(consts)))

        # Clear all marked objects
        for unit in objects_to_remove:
            um.remove_unit(unit=unit)

        # Clear all given objects
        for unit in units:
            um.remove_unit(unit=unit)
