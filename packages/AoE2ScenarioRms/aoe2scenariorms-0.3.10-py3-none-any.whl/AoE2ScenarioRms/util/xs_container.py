from __future__ import annotations

import copy
from typing import Dict, List

from AoE2ScenarioRms.enums import XsKey


class XsContainer:
    def __init__(self, entries: Dict[XsKey, List[str]] = None) -> None:
        """
        Class to hold, update and inject XS strings to set into a given script

        Args:
            entries: The key, value combinations to update and/or use to inject into a script
        """
        self.entries: Dict[XsKey, List[str]]

        self._set_entries(entries or {})

    def _set_entries(self, entries: Dict[XsKey, List[str]]):
        """Set the values to the given entries where possible"""
        self.entries: Dict[XsKey, List[str]] = {key: entries.get(key, []) for key in XsKey}

    def __add__(self, other: XsContainer):
        return XsContainer(self._add(other, True))

    def __iadd__(self, other: XsContainer):
        self._add(other, False)
        return self

    def _add(self, other: XsContainer, deepcopy: bool):
        """General implementation of addition for both __add__ and __iadd__."""
        if not isinstance(other, XsContainer):
            raise TypeError(f"Cannot add XsContainer with {other.__class__}")

        entries = copy.deepcopy(self.entries) if deepcopy else self.entries
        for key, val in other.entries.items():
            entries.setdefault(key, []).extend(val)
        return entries

    def resolve(self, script: str) -> str:
        """
        Resolve a script by replacing all keys present in this container with the corresponding values

        Args:
            script: The script to inject XS code into

        Returns:
            The updated script
        """
        for key in self.entries.keys():
            script = self.replace(script, key)
        return script

    def replace(self, script: str, key: XsKey) -> str:
        """
        Replace a REPLACE_KEY within a script with the value present in this container

        Args:
            script: The script to update
            key: The key to use for the update

        Returns:
            The updated script
        """
        join_string = XsKey.join_string(key)

        joined_lines = join_string + join_string.join(self.entries[key])
        return script.replace(f"""/* REPLACE:{key.name} */""", joined_lines)

    def init(self, key: XsKey) -> None:
        """Initialize (reset) a certain key"""
        self.set(key, [])

    def get(self, key: XsKey) -> List[str]:
        """Set an entry to a given value"""
        return self.entries[key]

    def set(self, key: XsKey, value: List[str]) -> None:
        """Set an entry to a given value"""
        self.entries[key] = value

    def append(self, key: XsKey, value: str) -> None:
        self.entries[key].append(value)

    def extend(self, key: XsKey, value: List[str]) -> None:
        self.entries[key].extend(value)
