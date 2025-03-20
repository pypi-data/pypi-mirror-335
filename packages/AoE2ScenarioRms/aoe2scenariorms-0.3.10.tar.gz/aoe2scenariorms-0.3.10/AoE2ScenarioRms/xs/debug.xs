

void printArray1D(int arrayId = -1)
{
    static int print_id = 0;
    int row = 0;
    string rowStr = "p" + print_id + " " + row + " [ ";
    while(row < xsArrayGetSize(arrayId))
    {
        rowStr = rowStr + " "+ xsArrayGetBool(arrayId, row) + " ";
        row++;
    }
    rowStr = rowStr + "]";
    xsChatData(rowStr);
    print_id++;
}
