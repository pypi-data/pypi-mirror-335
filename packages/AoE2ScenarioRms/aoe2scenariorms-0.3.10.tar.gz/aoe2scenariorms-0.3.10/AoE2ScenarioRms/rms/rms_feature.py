from abc import abstractmethod

from AoE2ScenarioParser.scenarios.aoe2_de_scenario import AoE2DEScenario

from AoE2ScenarioRms.util.xs_container import XsContainer
from AoE2ScenarioRms.util.grid_map import GridMap
from AoE2ScenarioRms.rms.rms_config import RmsConfig


class RmsFeature:
    """Super class for all RMS feature classes. Not (really) used (for now?)"""
    def __init__(self, scenario: AoE2DEScenario, xs_container: XsContainer) -> None:
        self.scenario: AoE2DEScenario = scenario
        self.xs_container: XsContainer = xs_container

    @abstractmethod
    def init(self, config: RmsConfig) -> None:
        ...

    @abstractmethod
    def build(self, config: RmsConfig, grid_map: GridMap) -> None:
        ...

    @abstractmethod
    def solve(self, config: RmsConfig, grid_map: GridMap):
        ...
