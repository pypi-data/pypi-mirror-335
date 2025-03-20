from __future__ import annotations

from typing import TYPE_CHECKING, List

from AoE2ScenarioParser.datasets.other import OtherInfo
from AoE2ScenarioParser.datasets.players import PlayerId
from AoE2ScenarioParser.objects.data_objects.trigger import Trigger
from AoE2ScenarioParser.scenarios.aoe2_de_scenario import AoE2DEScenario

from AoE2ScenarioRms.enums import XsKey
from AoE2ScenarioRms.errors import InvalidCreateObjectError
from AoE2ScenarioRms.rms.create_object.create_object_config import CreateObjectConfig
from AoE2ScenarioRms.rms.rms_feature import RmsFeature
from AoE2ScenarioRms.util import XsUtil, XsContainer, Locator

if TYPE_CHECKING:
    from AoE2ScenarioRms.util import GridMap


class CreateObjectFeature(RmsFeature):
    unique_names = set()

    def __init__(self, scenario: AoE2DEScenario, disable_all_trigger: Trigger) -> None:
        """
        Class that manages the functionality behind implementing the create_object clause

        Args:
            scenario: The scenario to apply the configs to
        """
        container = XsContainer()

        super().__init__(scenario, container)

        self.disable_all_trigger = disable_all_trigger

    def init(self, config: CreateObjectConfig) -> None:
        """
        Initialize the 'create object' configurations. Setting XS initializers like variable and array definitions

        Args:
            config: The configs to be added
        """
        name = self._name(config)

        self._validate_name_unique(name)

        self.xs_container.append(
            XsKey.RESOURCE_VARIABLE_DECLARATION,
            f"int {name} = {config.index};"
        )

        self.xs_container.append(
            XsKey.RESOURCE_GROUP_NAMES_DECLARATION,
            f"xsArraySetString(__RESOURCE_GROUP_NAMES, {name}, \"{config.name}\");"
        )

        self.xs_container.append(
            XsKey.RESOURCE_COUNT_DECLARATION,
            f"xsArraySetInt(__RESOURCE_SPAWN_COUNTS, {name}, {config.max_potential_group_count});"
        )

        self.xs_container.append(
            XsKey.RESOURCE_MAX_SPAWN_DECLARATION,
            f"xsArraySetFloat(__RESOURCE_MAX_SPAWN_COUNTS, {name}, {config.number_of_groups}.0);"
        )

        bool_ = XsUtil.bool(config.scale_to_player_number)
        self.xs_container.append(
            XsKey.RESOURCE_MAX_SPAWN_IS_PER_PLAYER_DECLARATION,
            f"xsArraySetBool(__RESOURCE_MAX_SPAWN_COUNTS_IS_PER_PLAYER, {name}, {bool_});"
        )

        self.xs_container.append(
            XsKey.RESOURCE_LOCATION_INJECTION,
            f"rArray = xsArrayGetInt(__ARRAY_RESOURCE_LOCATIONS, {name});"
        )

        self.xs_container.extend(
            XsKey.CONFIG_DECLARATION,
            [
                f"cArray = xsArrayGetInt(__ARRAY_RESOURCE_CONFIGS, {name});",
                f"xsArraySetInt(cArray, 0, {config.temp_min_distance_group_placement});",
                f"xsArraySetInt(cArray, 1, {config.min_distance_group_placement});",
            ]
        )

    def build(self, config: CreateObjectConfig, grid_map: 'GridMap') -> None:
        """
        Write the functional logic (triggers) for placing the objects. Also write the functional and conditional logic
        for XS for the given configs.

        Args:
            config: The config to implement
            grid_map: The GridMap to take into account when generating potential locations for groups
        """
        tm, um = self.scenario.trigger_manager, self.scenario.unit_manager
        name = self._name(config)

        groups = Locator.create_groups(config, grid_map)

        for index, group in enumerate(groups):
            spawn_group = tm.add_trigger(f"Spawn {config.name} {index}/{len(groups)}")
            self.disable_all_trigger.new_effect.deactivate_trigger(spawn_group.trigger_id)

            group_const = config.get_random_const()

            function = f"bool __should_spawn_{config.name}_{index}() {{" \
                f"return (xsArrayGetBool(xsArrayGetInt(__ARRAY_RESOURCE_PLACED_INDICES, {name}), {index}));" \
                f"}}"
            spawn_group.new_condition.script_call(xs_function=function.strip().replace('  ', ''))

            for iindex, tile in enumerate(group):
                spawn_group.new_effect.create_object(group_const, PlayerId.GAIA, tile.x, tile.y)

                if config.debug_place_all:
                    um.add_unit(PlayerId.GAIA, group_const, tile.x + .5, tile.y + .5)
                    player = PlayerId.GAIA if iindex == 0 else PlayerId.ONE
                    const = OtherInfo.FLAG_M.ID if iindex == 0 else OtherInfo.FLAG_C.ID
                    um.add_unit(player, const, tile.x + .5, tile.y + .5)

            self.xs_container.append(
                XsKey.RESOURCE_LOCATION_INJECTION,
                f"xsArraySetVector(rArray, {index}, vector({group[0].x}, {group[0].y}, -1));\t// {index}"
            )
        self.xs_container.append(
            XsKey.RESOURCE_LOCATION_INJECTION,
            f"ShuffleVectorArray(rArray, xsArrayGetInt(__ARRAY_RESOURCE_INDICES, {name}));"
        )

    def solve(self, configs: List[CreateObjectConfig], grid_map: 'GridMap') -> XsContainer:
        """
        Execute the init and build steps in one go for each config given.

        Args:
            configs: The configs to implement
            grid_map: The GridMap to take into account when generating potential locations for groups of configs

        Returns:
            The XsContainer with all generated XS
        """
        for config_entry in configs:
            self.init(config_entry)
            self.build(config_entry, grid_map)
        return self.xs_container

    @staticmethod
    def _validate_name_unique(name: str) -> None:
        """
        Validate if the given name is unique compared to other names used

        Args:
            name: The name to validate

        Raises:
            InvalidCreateObjectError: If the given name has already been registered before in the scenario
        """
        if name in CreateObjectConfig.unique_names:
            raise InvalidCreateObjectError(
                f"A CreateObjectFeature with the name '{name}' was already initialized. "
                f"Make sure the names are unique and are not accidentally registered more than once.\n"
                f"Also make sure that names aren't differentiated through just casing or spaces."
            )
        CreateObjectConfig.unique_names.add(name)

    @staticmethod
    def _name(create: CreateObjectConfig) -> str:
        return f"____{XsUtil.constant(create.name)}"
