/* REPLACE:RESOURCE_VARIABLE_DECLARATION */

int __RESOURCE_COUNT = /* REPLACE:RESOURCE_VARIABLE_COUNT */;
bool __RESOURCE_SPAWNING_READY = false;
bool __RESOURCE_SPAWNING_FINISHED = false;

// ---------< Other initialization stuff >--------- \\
/* REPLACE:XS_ON_INIT_FILE */

// ---------< Arrays where resource ID is value (1D) >--------- \\
// Amount of potential spawns per resource
int __RESOURCE_SPAWN_COUNTS = -1;
int __RESOURCE_MAX_SPAWN_COUNTS = -1;
int __RESOURCE_MAX_SPAWN_COUNTS_IS_PER_PLAYER = -1;
int __RESOURCE_GROUP_NAMES = -1;
int __RESOURCE_FINISHED_SPAWNING = -1;

// ---------< Arrays where resource ID is reference to other Array (2D) >--------- \\
// Arrays for locations
int __ARRAY_RESOURCE_LOCATIONS = -1;
int __ARRAY_RESOURCE_INDICES = -1;
int __ARRAY_RESOURCE_PLACED = -1;
int __ARRAY_RESOURCE_PLACED_INDICES = -1;
int __ARRAY_RESOURCE_CONFIGS = -1;          // [i][0]: dist self, [i][1]: dist other
int __ARRAY_RESOURCE_PROGRESS = -1;         // [i][0]: placed, [i][1]: skipped

// ---------< Functions >--------- \\
bool isReadyToSpawnResources() {
    return (__RESOURCE_SPAWNING_READY);
}

float getXyDistance(vector loc1 = vector(-1, -1, -1), vector loc2 = vector(-1, -1, -1)) {
    float x = pow(xsVectorGetX(loc1) - xsVectorGetX(loc2), 2.0);
    float y = pow(xsVectorGetY(loc1) - xsVectorGetY(loc2), 2.0);
    return (sqrt(x + y));
}

string getVectorAsString(vector loc = vector(-1, -1, -1)) {
    return ("x: " + xsVectorGetX(loc) + ", y:" + xsVectorGetY(loc));
}

bool spawnResource__024510896(int resourceId = -1) {
    if (resourceId == -1)
        return (false);

    int resourceSpawnCount = xsArrayGetInt(__RESOURCE_SPAWN_COUNTS, resourceId);
    float resourceMaxSpawnCount = xsArrayGetFloat(__RESOURCE_MAX_SPAWN_COUNTS, resourceId);

    if (xsArrayGetBool(__RESOURCE_MAX_SPAWN_COUNTS_IS_PER_PLAYER, resourceId)) {
        resourceMaxSpawnCount = resourceMaxSpawnCount * xsGetNumPlayers();
    }

    int resourceLocationsArray             = xsArrayGetInt(__ARRAY_RESOURCE_LOCATIONS, resourceId);
    int resourceIndicesArray               = xsArrayGetInt(__ARRAY_RESOURCE_INDICES, resourceId);
    int resourcePlacedLocationsArray       = xsArrayGetInt(__ARRAY_RESOURCE_PLACED, resourceId);
    int resourcePlacedLocationsIndiceArray = xsArrayGetInt(__ARRAY_RESOURCE_PLACED_INDICES, resourceId);
    int resourceConfigArray                = xsArrayGetInt(__ARRAY_RESOURCE_CONFIGS, resourceId);
    int progressArray                      = xsArrayGetInt(__ARRAY_RESOURCE_PROGRESS, resourceId);

    int placedResourcesCount = xsArrayGetInt(progressArray, 0);
    int skippedResourceCount = xsArrayGetInt(progressArray, 1);
    int startAtIndex = placedResourcesCount + skippedResourceCount;

    int minimumDistToSelf = xsArrayGetInt(resourceConfigArray, 0);
    int minimumDistToOther = xsArrayGetInt(resourceConfigArray, 1);

    for (i = startAtIndex; < resourceSpawnCount) {
        Vector v = xsArrayGetVector(resourceLocationsArray, i);
        
        bool allowed = true;
    	for (r = 0; < __RESOURCE_COUNT) {
			int minDistance = minimumDistToOther;
			if (r == resourceId) {
				minDistance = minimumDistToSelf;
            }

			int otherPlacedLocArray = xsArrayGetInt(__ARRAY_RESOURCE_PLACED, r);
            int otherProgressArray = xsArrayGetInt(__ARRAY_RESOURCE_PROGRESS, r);

            int otherPlacedResourcesCount = xsArrayGetInt(otherProgressArray, 0);
			
			bool finished = false;
			for (j = 0; < otherPlacedResourcesCount) {
            	Vector v2 = xsArrayGetVector(otherPlacedLocArray, j);

                float d = getXyDistance(v, v2);
				if (d < minDistance) {
					allowed = false;
					finished = true;
					break;
				}
			}
			
			if (finished) {
				break;
			}
		}

        if (allowed) {
            xsArraySetBool(resourcePlacedLocationsIndiceArray, xsArrayGetInt(resourceIndicesArray, i), true);
            xsArraySetVector(resourcePlacedLocationsArray, placedResourcesCount, v);
            xsArraySetInt(progressArray, 0, placedResourcesCount + 1);
            
            /* REPLACE:XS_ON_SUCCESSFUL_SPAWN */
            
            if (placedResourcesCount + 1 >= resourceMaxSpawnCount) {
                // Next NOT allowed to be placed. Max is reached.
                return (false);
            }
            
            // Next allowed to be placed because end is not reached yet
            return (true);
        } else {
            xsArraySetInt(progressArray, 1, skippedResourceCount + 1);
        }
    }

    // Next NOT allowed to be placed because the end is reached. Nothing fits anymore.
    return (false);
}

bool spawnAllOfResource__895621354(int resourceId = -1) {
    if (__RESOURCE_SPAWNING_READY == false) {
        return (false);
    }

    bool b = true;
    while (b) {
        b = spawnResource__024510896(resourceId);
    }

    /* REPLACE:AFTER_RESOURCE_SPAWN_EVENT */

    xsArraySetBool(__RESOURCE_FINISHED_SPAWNING, resourceId, true);

    /* Verify that all resources finished spawning so triggers can be disabled */
    bool allFinished = true;
    for (i = 0; < __RESOURCE_COUNT) {
        if (xsArrayGetBool(__RESOURCE_FINISHED_SPAWNING, i) == false) {
            allFinished = false;
            break;
        }
    }

    if (allFinished) {
        __RESOURCE_SPAWNING_FINISHED = true;

        /* REPLACE:AFTER_ALL_RESOURCES_SPAWNED_EVENT */
    }

    return (true);
}

rule main_initialise__023658412
    active
    runImmediately
    minInterval 1
    maxInterval 1
    priority 1000
{
/* REPLACE:XS_ON_INIT_RULE */

    __RESOURCE_GROUP_NAMES = xsArrayCreateString(__RESOURCE_COUNT, "", "__RESOURCE_GROUP_NAMES__594522389");
/* REPLACE:RESOURCE_GROUP_NAMES_DECLARATION */

    __RESOURCE_SPAWN_COUNTS = xsArrayCreateInt(__RESOURCE_COUNT, -1, "__RESOURCE_SPAWN_COUNTS__538652012");
/* REPLACE:RESOURCE_COUNT_DECLARATION */

    __RESOURCE_MAX_SPAWN_COUNTS = xsArrayCreateFloat(__RESOURCE_COUNT, -1.0, "__RESOURCE_MAX_SPAWN_COUNTS__503956013");
/* REPLACE:RESOURCE_MAX_SPAWN_DECLARATION */

    __RESOURCE_MAX_SPAWN_COUNTS_IS_PER_PLAYER = xsArrayCreateBool(__RESOURCE_COUNT, false, "__RESOURCE_MAX_SPAWN_COUNTS_IS_PER_PLAYER__024698552");
/* REPLACE:RESOURCE_MAX_SPAWN_IS_PER_PLAYER_DECLARATION */

    __RESOURCE_FINISHED_SPAWNING    = xsArrayCreateBool(__RESOURCE_COUNT, false, "__RESOURCE_FINISHED_SPAWNING__664401567");

    __ARRAY_RESOURCE_LOCATIONS      = xsArrayCreateInt(__RESOURCE_COUNT, -1, "__ARRAY_RESOURCE_LOCATIONS__056985215");
    __ARRAY_RESOURCE_INDICES        = xsArrayCreateInt(__RESOURCE_COUNT, -1, "__ARRAY_RESOURCE_INDICES__021548785");
    __ARRAY_RESOURCE_PLACED         = xsArrayCreateInt(__RESOURCE_COUNT, -1, "__ARRAY_RESOURCE_PLACED__542150369");
    __ARRAY_RESOURCE_PLACED_INDICES = xsArrayCreateInt(__RESOURCE_COUNT, -1, "__ARRAY_RESOURCE_PLACED_INDICES__520001548");
    __ARRAY_RESOURCE_CONFIGS        = xsArrayCreateInt(__RESOURCE_COUNT, -1, "__ARRAY_RESOURCE_CONFIGS__522094889");
    __ARRAY_RESOURCE_PROGRESS       = xsArrayCreateInt(__RESOURCE_COUNT, -1, "__ARRAY_RESOURCE_PROGRESS__510369984");

    for (i = 0; < __RESOURCE_COUNT) {
        int count = xsArrayGetInt(__RESOURCE_SPAWN_COUNTS, i);

        int resourceArray        = xsArrayCreateVector(count, vector(-1, -1, -1), "resourceArray__352901574__v" + i);
        int indexArray           = xsArrayCreateInt(count, -1, "indexArray__456875221__v" + i);
        int resourcePlaced       = xsArrayCreateVector(count, vector(-1, -1, -1), "resourcePlaced__548476523__v" + i);
        int resourceIndicePlaced = xsArrayCreateBool(count, false, "resourceIndicePlaced__301548796__v" + i);
        int resourceConfig       = xsArrayCreateInt(2, -1, "resourceConfig__985256327__v" + i);
        int resourceProgress     = xsArrayCreateInt(2, 0, "resourceProgress__524875963__v" + i);

        for (ii = 0; < count) {
            xsArraySetInt(indexArray, ii, ii);
        }

        xsArraySetInt(__ARRAY_RESOURCE_LOCATIONS,      i, resourceArray);
        xsArraySetInt(__ARRAY_RESOURCE_INDICES,        i, indexArray);
        xsArraySetInt(__ARRAY_RESOURCE_PLACED,         i, resourcePlaced);
        xsArraySetInt(__ARRAY_RESOURCE_PLACED_INDICES, i, resourceIndicePlaced);
        xsArraySetInt(__ARRAY_RESOURCE_CONFIGS,        i, resourceConfig);
        xsArraySetInt(__ARRAY_RESOURCE_PROGRESS,       i, resourceProgress);
    }
    int cArray = -1;
/* REPLACE:CONFIG_DECLARATION */

    int rArray = -1;
/* REPLACE:RESOURCE_LOCATION_INJECTION */

    __RESOURCE_SPAWNING_READY = true;
    xsDisableSelf();
}
