from typing import TYPE_CHECKING

from AoE2ScenarioRms.debug.apply_debug import ApplyDebug

if TYPE_CHECKING:
    from AoE2ScenarioRms import AoE2ScenarioRms


class ApplyNoClutter(ApplyDebug):
    """

    Set the entire map to have no elevation or layered terrain for extra clarity

    """

    def __init__(self, rms: 'AoE2ScenarioRms') -> None:
        super().__init__(rms)

        for tile in rms.scenario.map_manager.terrain:
            tile.layer = -1
            tile.elevation = 1
