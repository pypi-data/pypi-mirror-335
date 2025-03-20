from AoE2ScenarioParser.exceptions.asp_warnings import AoE2ScenarioParserWarning


class AoE2ScenarioRmsError(AoE2ScenarioParserWarning):
    pass


class ImproperCreateObjectWarning(AoE2ScenarioRmsError):
    pass


class SpawnFailureWarning(AoE2ScenarioRmsError):
    pass
