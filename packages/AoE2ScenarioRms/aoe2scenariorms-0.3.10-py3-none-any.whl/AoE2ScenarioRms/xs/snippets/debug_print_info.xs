int progressArray = xsArrayGetInt(__ARRAY_RESOURCE_PROGRESS, resourceId);
string name = xsArrayGetString(__RESOURCE_GROUP_NAMES, resourceId);
int placedResourcesCount = xsArrayGetInt(progressArray, 0);

xsChatData("Group '" + name + "' (" + resourceId + ") spawned " + placedResourcesCount + " successfully!");
