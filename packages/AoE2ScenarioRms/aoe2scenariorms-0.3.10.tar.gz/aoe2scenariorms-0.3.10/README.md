# AoE2ScenarioRms

Add replay-ability to scenarios through random resource placement using triggers & XS!
A library built on top of the [AoE2ScenarioParser].

> Keep in mind this project is a **work-in-progress**

[AoE2ScenarioParser]: https://github.com/KSneijders/AoE2ScenarioParser

## Quick Links

- [Installation](#installation)
- [How to get started](#how-to-get-started)
- [Examples](#examples)

## Installation

You can install the project using **pip**:

```bash
pip install AoE2ScenarioRms
```

## Updating AoE2ScenarioRms

If you have the library already installed, you can use the following command to update it:

```bash
pip install --no-cache-dir --upgrade AoE2ScenarioRms
```

To read about the changes between versions, checkout the [CHANGELOG.md](./CHANGELOG.md) file.

## How to get started

_For examples, see the [Examples](#examples) header._

### 1. AoE2ScenarioRms

The first thing you do is wrap a `AoE2DEScenario` object from the `AoE2ScenarioParser`.  
For more info on the `AoE2ScenarioParser`,
click [here](https://ksneijders.github.io/AoE2ScenarioParser/getting_started/).

```py
from AoE2ScenarioParser.scenarios.aoe2_de_scenario import AoE2DEScenario
from AoE2ScenarioRms import AoE2ScenarioRms
...
scenario = AoE2DEScenario.from_file("<file-path here>")
asr = AoE2ScenarioRms(scenario)
```

Now `AoE2ScenarioRms` can access the scenario and start adding triggers and XS to it for random resources!

### 2. Clearing the scenario

When you have a scenario that you want filled with random resources, it makes sense you'd want the scenario to not
contain any resources to begin with. You can clear these using the `ScenarioUtil.clear(...)` functionality.

For example, if you want to clear absolutely everything that *can* be cleared, you can do the following:

```py
from AoE2ScenarioRms.util import ScenarioUtil
from AoE2ScenarioRms.flags import ObjectClear
...
ScenarioUtil.clear(scenario, ObjectClear.ALL)
```

Above you can see `ObjectClear.ALL` being used. This is quite a nuclear option, it might clear more than you want.  
Below is a list of things that can be cleared (and thus which `ObjectClear.ALL` clears).

- `ObjectClear.PLAYERS` - Remove all player related object (TCs, villagers, scouts etc.)
- `ObjectClear.BOARS` - Remove all boar-like units (e.g. Boar, Elephant, Rhinos...)
- `ObjectClear.SHEEP` - Remove all sheep-like units (e.g. Sheep, Goat, Turkey...)
- `ObjectClear.DEER` - Remove all deer-like units (e.g. Deer, Zebra, Ibex...) 
- `ObjectClear.WOLFS` - Remove all wolf-like units (e.g. Wolf, Crocodile, Lion...)
- `ObjectClear.GOLDS` - Remove all gold mines
- `ObjectClear.STONES` - Remove all stone mines
- `ObjectClear.BUSHES` - Remove all berry and fruit bushes
- `ObjectClear.STRAGGLERS` - Remove all trees not on tree terrain
- `ObjectClear.RELICS` - Remove all relics
- `ObjectClear.CLIFFS` - Remove all cliffs
- `ObjectClear.DEEP_FISH` - Remove all types of deep fish (including Dolphin and Great Marlins)
- `ObjectClear.SHORE_FISH` - Remove all shore fish and box turtles

There are also combinations of the above for ease of use:

- `ObjectClear.ANIMAL_OBJECTS` = `BOARS` + `SHEEP` + `DEER` + `WOLFS`
- `ObjectClear.FISH_OBJECTS` = `DEEP_FISH` + `SHORE_FISH`
- `ObjectClear.RESOURCE_OBJECTS` = `GOLDS` + `STONES` + `BUSHES` + `STRAGGLERS` + `RELICS`
- `ObjectClear.ALL` = Everything listed above

The object `ObjectClear` is a `Flag` object. This object has some special properties:

- You can combine them using `X | Y`: `ObjectClear.STONES | ObjectClear.GOLDS`  
  - This would clear all stone and gold tiles.
- You can exclude an option from a combination using `X & ~Y`: `ObjectClear.ALL & ~ObjectClear.CLIFFS`
  - This would clear everything listed above **except** cliffs.

So, to clear all animal objects but leave wolfs and also clear relics use the following:

```py
from AoE2ScenarioRms.util import ScenarioUtil
from AoE2ScenarioRms.flags import ObjectClear
...
object_clear = (ObjectClear.ANIMAL_OBJECTS & ~ObjectClear.WOLFS) | ObjectClear.RELICS
ScenarioUtil.clear(scenario, object_clear)
```


More info about `Flag` objects can be found on the [Python docs](https://docs.python.org/3/library/enum.html#enum.Flag).

### 3. GridMap

The spawning of objects (units, resources etc.) works by first creating a so called `GridMap`.  
A `GridMap` is used to store on which tiles the objects can (or cannot) spawn.  
For example, you can 'tell' a `GridMap` to only allow the spawning of objects on water terrains.

You can create a `GridMap` using the `GridMapFactory` like so:

```py
from AoE2ScenarioRms.util import GridMapFactory

...
GridMapFactory.select(...)  # Or
GridMapFactory.block(...)
```

The `select` and `block` functions can be used to either `select` certain tiles, or... to `block` them.  
Selecting tiles means an object can spawn on them and on nothing else, blocking them means the object **cannot** spawn
on the tiles, but they can on all others.

So, to follow the example above of only allowing spawning on water tiles you can do the following:

```py
from AoE2ScenarioParser.datasets.terrains import TerrainId
from AoE2ScenarioRms.util import GridMapFactory

...
grid_map = GridMapFactory.select(
    scenario=scenario,  # The `scenario` from AoE2DEScenario.from_file(...)
    terrain_ids=TerrainId.water_terrains()
)
```

This takes all types of water from a dataset in the `AoE2ScenarioParser` and adds them as `terrain_ids`.  
The function used is `select(...)` which means all objects you spawn with this `GridMap` will be spawned on water tiles.

The following methods of selecting which tiles to spawn objects on can be used:

| Attribute       | Description                                                                                                              |
|-----------------|--------------------------------------------------------------------------------------------------------------------------|
| `terrain_ids`   | (As seen above) - A `list` of terrain IDs to select/block. [Terrain Ids]                                                 |
| `terrain_marks` | A Flag that has 'shortcuts' to certain terrain aspects on a map. [TerrainMarks]                                          |
| `object_marks`  | A Flag that has 'shortcuts' to certain object aspects on a map. [ObjectMarks]                                            |
| `object_consts` | A `dict` of object consts as keys and a distance as value that to select/block around the given objects. [Object consts] |

[Terrain Ids]: #terrain-ids
[TerrainMarks]: #terrainmarks
[ObjectMarks]: #objectmarks
[Object consts]: #object-consts

#### Terrain Ids

Todo -- Please check out the example for now: [Examples](https://github.com/KSneijders/AoE2ScenarioRms/tree/main/examples).

#### TerrainMarks

Todo -- Please check out the example for now: [Examples](https://github.com/KSneijders/AoE2ScenarioRms/tree/main/examples).

#### ObjectMarks

Todo -- Please check out the example for now: [Examples](https://github.com/KSneijders/AoE2ScenarioRms/tree/main/examples).

#### Object consts

Todo -- Please check out the example for now: [Examples](https://github.com/KSneijders/AoE2ScenarioRms/tree/main/examples).

### 4. Create Objects

Todo -- Please check out the example for now: [Examples](https://github.com/KSneijders/AoE2ScenarioRms/tree/main/examples).

## Examples

Please check out the example [here](https://github.com/KSneijders/AoE2ScenarioRms/tree/main/examples).
(no _real_ docs atm)

## Ideas for future releases:

- Player areas :monkaS:
- Scale with map size (hardcoded on parser level as map_size cannot be changed dynamically)
- **v0.2.0** ~~Support larger objects (currently only 1x1 is supported)~~
- Automatically figure out what to remove based on CreateObjectConfig configs
- Add ability to mock the XS spawning process to estimate the amount of necessary successful spawn attempts
- Ability to bind ID to list of create objects and be able to differentiate distance to each group
- (Somehow) remove spawn order bias. Currently, the earlier the spawns the more chance they have to succeed because
- the map isn't filled up yet.
- ...

---

**Suggestions are always welcome!**

# Authors

- Kerwin Sneijders (Main Author)

# License

MIT License: Please see the [LICENSE file].

[license file]: https://github.com/KSneijders/AoE2ScenarioRms/blob/main/LICENSE
