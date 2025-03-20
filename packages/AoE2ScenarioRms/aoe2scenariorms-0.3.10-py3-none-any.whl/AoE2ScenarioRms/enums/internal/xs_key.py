from __future__ import annotations

from enum import Enum, auto


class XsKey(Enum):
    """
    Enum used to identify the different sections of an XS script that can be replaced.
    Only really useful in conjunction with ``XsContainer``
    """
    RESOURCE_VARIABLE_DECLARATION = auto()
    RESOURCE_VARIABLE_COUNT = auto()
    RESOURCE_COUNT_DECLARATION = auto()
    RESOURCE_MAX_SPAWN_DECLARATION = auto()
    RESOURCE_MAX_SPAWN_IS_PER_PLAYER_DECLARATION = auto()
    RESOURCE_LOCATION_INJECTION = auto()
    RESOURCE_GROUP_NAMES_DECLARATION = auto()

    CONFIG_DECLARATION = auto()

    AFTER_RESOURCE_SPAWN_EVENT = auto()
    AFTER_ALL_RESOURCES_SPAWNED_EVENT = auto()

    XS_ON_INIT_FILE = auto()
    XS_ON_INIT_RULE = auto()

    XS_ON_SUCCESSFUL_SPAWN = auto()

    @staticmethod
    def join_string(key: XsKey):
        return _xs_join_strings[key]


_tab = ' ' * 4
_xs_join_strings = {
    XsKey.RESOURCE_VARIABLE_COUNT: '',

    XsKey.RESOURCE_VARIABLE_DECLARATION: '\n',
    XsKey.XS_ON_INIT_FILE: '\n',

    XsKey.RESOURCE_GROUP_NAMES_DECLARATION: f'\n{_tab}',
    XsKey.RESOURCE_COUNT_DECLARATION: f'\n{_tab}',
    XsKey.RESOURCE_MAX_SPAWN_DECLARATION: f'\n{_tab}',
    XsKey.RESOURCE_MAX_SPAWN_IS_PER_PLAYER_DECLARATION: f'\n{_tab}',
    XsKey.RESOURCE_LOCATION_INJECTION: f'\n{_tab}',
    XsKey.CONFIG_DECLARATION: f'\n{_tab}',
    XsKey.XS_ON_INIT_RULE: f'\n{_tab}',

    XsKey.AFTER_RESOURCE_SPAWN_EVENT: f'\n{_tab}',
    XsKey.AFTER_ALL_RESOURCES_SPAWNED_EVENT: f'\n{_tab}{_tab}',

    XsKey.XS_ON_SUCCESSFUL_SPAWN: f'\n{_tab}{_tab}{_tab}',
}
