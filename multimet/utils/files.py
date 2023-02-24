
import numpy as np
import json
from typing import Sequence

def jsonify(data_dict):
    res = dict(data_dict)
    for key, item in res.items():
        if isinstance(item, np.ndarray):
            res[key] = item.tolist()
    return res

def numpify(data_dict):
    res = dict(data_dict)
    for key, item in res.items():
        if isinstance(item, list):
            res[key] = np.array(item)
    return res

def serialize(obj):
    # To check if the object is serializable
    try:
        json.dumps(obj)
        return obj
    except (TypeError, OverflowError):
        if isinstance(obj, Sequence):
            res = [serialize(x) for x in obj]
        # If we are dealing with a dict of object
        elif isinstance(obj, dict):
            res = {key : serialize(item) for key, item in obj.items()}
        # If we are dealing with a dict of object
        elif isinstance(obj, np.ndarray):
            res = obj.tolist()
        else:
            res =  jsonify(obj)
        return res

def save_as_json(obj, filename, path=""):
    """
    Safely save object as a valid json
    """
    # make the object serializable
    class_dict = serialize(obj)
    # convert into a string representing a valid jsonfile
    json_str = json.dumps(class_dict, indent=4)
    if filename[-5:] != ".json":
        filename += ".json"
    with open(path + filename, 'w', encoding='utf-8') as f:
        # save
        f.write(json_str)

def clear_double_space(filename):
    # Read in the file
    with open(filename, 'r') as file :
        filedata_origin = file.read()

    # Replace the target string
    filedata_final = filedata_origin.replace('  ', ' ')

    # Write the file out again
    if filedata_final != filedata_origin:
        with open(filename, 'w') as file:
            file.write(filedata_final)