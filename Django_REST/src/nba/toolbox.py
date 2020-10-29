#########################################################################
# Useful functions
#########################################################################

# Print in lines
def PrintInLines(arr):
    print(*arr, sep='\n')
    return None


# return headers, data
def HeaderDataReturn(robj):
    dataset = robj.get_dict()
    headers, data = dataset["headers"], dataset["data"]
    # no return value
    if (len(data)==0):
        print('No Values')
        return ([], [])
    # if there is one return set / rows
    elif (len(data)==1):
        data = data[0]
        return (headers, data)
    # if there are multiple return sets / rows
    else:
        return headers, data

# function to simplify extracting the data from the return
# dataset
def DataReturn(robj):
    dataset = robj.get_dict()
    headers, data = dataset["headers"], dataset["data"]
    if (len(data) == 0):            # no return value
        print('No Values')
        return []
    elif (len( data ) == 1):        # one row
        return data[0]
    else:                           # multiple rows
        print(f'data len = {len(data)}')
        return data