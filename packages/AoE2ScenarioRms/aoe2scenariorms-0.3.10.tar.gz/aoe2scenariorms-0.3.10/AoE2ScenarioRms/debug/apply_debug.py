from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from AoE2ScenarioRms import AoE2ScenarioRms


class ApplyDebug:
    """

    Base class for all 'debug appliers'

    """

    def __init__(self, rms: 'AoE2ScenarioRms') -> None:
        super().__init__()

        rms._debug_applied = True
