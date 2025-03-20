from typing import TYPE_CHECKING

from AoE2ScenarioParser.datasets.other import OtherInfo
from AoE2ScenarioParser.datasets.players import PlayerId

from AoE2ScenarioRms.debug.apply_debug import ApplyDebug
from AoE2ScenarioRms.enums import XsKey
from AoE2ScenarioRms.util import XsUtil

if TYPE_CHECKING:
    from AoE2ScenarioRms import AoE2ScenarioRms


class ApplyXsPrint(ApplyDebug):
    """

    When testing (in game: load scenario > test), the amount of resources that were able to spawn is printed in the chat

    """

    def __init__(self, rms: 'AoE2ScenarioRms') -> None:
        super().__init__(rms)

        rms.xs_container.extend(
            XsKey.AFTER_RESOURCE_SPAWN_EVENT,
            XsUtil.file('snippets/debug_print_info.xs').splitlines()
        )

        rms.xs_container.append(
            XsKey.AFTER_RESOURCE_SPAWN_EVENT,
            'xsChatData("All resources finished spawning!");'
        )

        rms._disable_all_trigger.new_effect.display_instructions(
            object_list_unit_id=OtherInfo.RELIC.ID,
            source_player=PlayerId.ONE,
            message="All resources finished spawning!"
        )
