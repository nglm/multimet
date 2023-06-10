import numpy as np
from typing import List, Sequence, Union, Any, Dict

def standardize(
    list_var,  # List[ndarray(n_members, n_time, n_long, n_lat)]
    each_loc: bool = False, # if true return List[ndarray(n_long, n_lat)] else return List[Scaler]
):

    #FIXME: Outdated since multivariate

    list_scalers = []
    list_stand_var = []
    for var in list_var:
        if len(var.shape) > 2:
            (n_members, n_time, n_long, n_lat) = var.shape
        else:
            (n_members, n_time) = var.shape
            each_loc = False
        if each_loc:
            print("Not implemented yet")
        else:
            if len(var.shape) > 2:
                print("Not implemented yet")
            else:
                mean = np.mean(var)
                std = np.std(var)
                list_stand_var.append((var - mean) / std)
                list_scalers.append([mean, std])
    return (list_scalers, list_stand_var)

def get_list_std(
    list_var,  # list_var: list of ndarray(n_members, n_time,  [n_long, n_lat])
):
    list_std=[]
    # find std values for each variable at each time step
    for var in list_var:
        #std = np.squeeze(np.std(var,axis=0, keepdims=True))
        std = np.squeeze(np.std(var,axis=0))
        list_std.append(std)
    # return List[ndarray(n_time, [n_long, n_lat])]
    return(list_std)

def get_list_average_values(
    list_values,  # List[ndarray(n_time, n_long, n_lat)]
):
    list_average_values = []
    for values in list_values:
        average_values = np.mean(values, axis=(1,2))
        list_average_values.append(average_values)
    #list_average_values: List[ndarray(n_time)]
    return list_average_values

