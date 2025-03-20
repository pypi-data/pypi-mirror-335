from enum import IntFlag, auto


class ObjectClear(IntFlag):
    """Flag used for clearing specific aspects of a scenario"""
    PLAYERS = auto()
    """Clear any player related object"""
    BOARS = auto()
    """Clear all boars and boar-like animals (i.e. Elephants & Rhinos)"""
    SHEEP = auto()
    """Clear all sheep and sheep-like animals (i.e. Goats & Llamas)"""
    DEER = auto()
    """Clear all deer and deer-like animals (i.e. Zebras & IBEX)"""
    WOLFS = auto()
    """Clear all wolfs and wolf-like animals (i.e. Crocodile & Snow leopard)"""
    GOLDS = auto()
    """Clear all gold tiles"""
    STONES = auto()
    """Clear all stone tiles"""
    BUSHES = auto()
    """Clear both forage and fruit bushes"""
    STRAGGLERS = auto()
    """Clear straggler trees (trees that are not on 'tree terrain')"""
    RELICS = auto()
    """Clear all relics"""
    CLIFFS = auto()
    """Clear all cliffs"""
    DEEP_FISH = auto()
    """Clear all types of deep fish including dolphins and great fish marlin"""
    SHORE_FISH = auto()
    """Clear both shore fish and box turtles"""

    ANIMAL_OBJECTS = BOARS | SHEEP | DEER | WOLFS
    """Clear all land animals objects"""
    FISH_OBJECTS = DEEP_FISH | SHORE_FISH
    """Clear all fish objects"""
    RESOURCE_OBJECTS = GOLDS | STONES | BUSHES | STRAGGLERS | RELICS
    """Clear all resources objects (note that this does not include ``ANIMAL_OBJECTS`` & ``FISH_OBJECTS``)"""
    ALL = ANIMAL_OBJECTS | FISH_OBJECTS | RESOURCE_OBJECTS | PLAYERS | CLIFFS
    """
    Clear all animals on land and water, all resource objects (including relics), all player related objects and all 
    cliffs
    """
