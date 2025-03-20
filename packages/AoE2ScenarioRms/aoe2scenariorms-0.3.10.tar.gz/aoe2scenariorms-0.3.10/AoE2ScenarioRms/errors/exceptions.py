from AoE2ScenarioParser.exceptions.asp_exceptions import AoE2ScenarioParserError


class AoE2ScenarioRmsError(AoE2ScenarioParserError):
    pass


class LocationNotFoundError(AoE2ScenarioRmsError):
    pass


class InvalidCreateObjectError(AoE2ScenarioRmsError):
    pass


class InvalidAoE2ScenarioRmsState(AoE2ScenarioRmsError):
    pass
