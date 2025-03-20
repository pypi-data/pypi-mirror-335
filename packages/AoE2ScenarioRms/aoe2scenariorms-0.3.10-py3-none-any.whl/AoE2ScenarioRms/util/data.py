from typing import List

from AoE2ScenarioParser.datasets.other import OtherInfo
from AoE2ScenarioParser.datasets.terrains import TerrainId
from AoE2ScenarioParser.datasets.units import UnitInfo

from AoE2ScenarioRms.flags.object_clear import ObjectClear
from AoE2ScenarioRms.flags.terrain_mark import TerrainMark


class Data:
    """
    Static class that holds functions that return specific data, mainly IDs used for removal of objects or marking of a
    scenario.
    """
    @staticmethod
    def trees() -> List[int]:
        """
        Returns:
            A list of all tree object IDs
        """
        return [o.ID for o in OtherInfo.trees()]

    @staticmethod
    def cliffs() -> List[int]:
        """
        Returns:
            A list of all cliff IDs
        """
        return [
            264, 265, 266, 267, 268, 269, 270, 271, 272,
            1339, 1340, 1341, 1342, 1344, 1346
        ]

    @staticmethod
    def get_terrain_ids_by_terrain_marks(marks: TerrainMark) -> List[TerrainId]:
        """
        Args:
            marks: The marks to take into account

        Returns:
            A list of Terrain Ids based on the marks given
        """
        ids: List[TerrainId] = []

        if TerrainMark.WATER in marks:
            ids.extend(TerrainId.water_terrains())
        if TerrainMark.BEACH in marks:
            ids.extend(TerrainId.beach_terrains())
        if TerrainMark.LAND in marks:
            water_beach = TerrainId.water_terrains() + TerrainId.beach_terrains()
            ids.extend(terrain for terrain in TerrainId if terrain not in water_beach)

        return ids

    @staticmethod
    def get_object_consts_by_clear_options(clear: ObjectClear) -> List[int]:
        """
        Args:
            clear: The ``ObjectClear`` configuration used for removing objects from a scenario

        Returns:
            A list of IDs of object consts used for the removal of objects
        """
        consts: List[int] = []

        if ObjectClear.BOARS in clear:
            consts.extend([
                UnitInfo.JAVELINA.ID,
                UnitInfo.WILD_BOAR.ID,
                UnitInfo.ELEPHANT.ID,
                UnitInfo.RHINOCEROS.ID
            ])

        if ObjectClear.SHEEP in clear:
            consts.extend([
                UnitInfo.SHEEP.ID,
                UnitInfo.GOAT.ID,
                UnitInfo.TURKEY.ID,
                UnitInfo.GOOSE.ID,
                UnitInfo.PIG.ID,
                UnitInfo.COW_A.ID,
                UnitInfo.COW_B.ID,
                UnitInfo.COW_C.ID,
                UnitInfo.COW_D.ID,
                UnitInfo.LLAMA.ID
            ])

        if ObjectClear.DEER in clear:
            consts.extend([
                UnitInfo.DEER.ID,
                UnitInfo.IBEX.ID,
                UnitInfo.ZEBRA.ID
            ])

        if ObjectClear.WOLFS in clear:
            consts.extend([
                UnitInfo.WOLF.ID,
                UnitInfo.JAGUAR.ID,
                UnitInfo.LION.ID,
                UnitInfo.SNOW_LEOPARD.ID,
                UnitInfo.CROCODILE.ID,
                UnitInfo.BEAR.ID,
            ])

        if ObjectClear.RELICS in clear:
            consts.append(OtherInfo.RELIC.ID)

        if ObjectClear.GOLDS in clear:
            consts.append(OtherInfo.GOLD_MINE.ID)

        if ObjectClear.STONES in clear:
            consts.append(OtherInfo.STONE_MINE.ID)

        if ObjectClear.BUSHES in clear:
            consts.extend([
                OtherInfo.FORAGE_BUSH.ID,
                OtherInfo.FRUIT_BUSH.ID
            ])

        if ObjectClear.CLIFFS in clear:
            consts.extend(Data.cliffs())

        if ObjectClear.DEEP_FISH in clear:
            consts.extend([
                OtherInfo.FISH_TUNA.ID,
                OtherInfo.FISH_PERCH.ID,
                OtherInfo.FISH_DORADO.ID,
                OtherInfo.FISH_SALMON.ID,
                OtherInfo.FISH_SNAPPER.ID,
                OtherInfo.GREAT_FISH_MARLIN.ID,
                OtherInfo.DOLPHIN.ID,
            ])

        if ObjectClear.SHORE_FISH in clear:
            consts.extend([
                OtherInfo.SHORE_FISH.ID,
                OtherInfo.BOX_TURTLES.ID,
            ])

        return consts
