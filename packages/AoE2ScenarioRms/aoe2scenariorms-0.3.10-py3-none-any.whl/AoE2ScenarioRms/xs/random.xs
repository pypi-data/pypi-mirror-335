int __randomSeed = 0;
int __randomModulus = 0;
int __randomMultiplier = 0;
int __randomIncrement = 0;

int Abs(int value=0){
    if(value < 0)
        return (value * -1);
    return (value);
}

int GetRandom(){
    __randomSeed = Abs((__randomMultiplier * __randomSeed + __randomIncrement) % __randomModulus);
    return (__randomSeed);
}

int GetRandomRange(int min=0,int max=999999999){
    return ((GetRandom() % (max+1-min)) + min);
}


rule main_initialise_rng__061843574
    active
    runImmediately
    minInterval 1
    maxInterval 1
    priority 1000
{
    __randomSeed = xsGetRandomNumber()*xsGetRandomNumber();
    __randomModulus = 0.0 + pow(2.0,31.0);
    __randomMultiplier = 999999999 + 103515246;
    __randomIncrement = 12345;

    xsDisableSelf();
}

void ShuffleVectorArray(int arr = -1, int indexArr = -1) {
    if (arr == -1)
        return;
    
    int n = xsArrayGetSize(arr);
    for (i = 0; < n) {
        int j = GetRandomRange(0, n - 1);
        Vector v = xsArrayGetVector(arr, j);
        int index = xsArrayGetInt(indexArr, j);
        xsArraySetVector(arr, j, xsArrayGetVector(arr, i));
        xsArraySetVector(arr, i, v);
        
        xsArraySetInt(indexArr, j, xsArrayGetInt(indexArr, i));
        xsArraySetInt(indexArr, i, index);
    }
}
