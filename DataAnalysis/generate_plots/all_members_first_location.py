#!/usr/bin/env python3
import sys
import os
from os import listdir, makedirs
import numpy as np
import matplotlib.pyplot as plt

sys.path.insert(1, os.path.join(sys.path[0], '..'))
sys.path.insert(1, os.path.join(sys.path[0], '../..'))

from statistics import preprocess_data
from utils.plt import from_list_to_subplots

# ---------------------------------------------------------
# Parameters:
# ---------------------------------------------------------

# Absolute path to the files
# type: str
PATH_DATA = "/home/natacha/Documents/Work/Data/Bergen/"

# Choose the path where the figs will be saved
# type: str
PATH_FIG= "/home/natacha/Documents/tmp/figs/all_members_first_location/"

# Choose which variables should be ploted
# type: List(str)
# Available variables:
# --- 2 metre temperature (“t2m”),
# --- 2m-Dew point temperature (“d2m”),
# --- Mean sea-level pressure (“msl”),
# --- 10m-winds in East and North direction (“u10”, “v10”)
# --- total water vapour in the entire column above the grid point (“tcwv”)
# if None: var_names = ["t2m","d2m","msl","u10","v10","tcwv"]
var_names=['t2m']
# Choose which instants should be ploted
# type: ndarray(int)
ind_time=None
# Choose which members should be ploted
# type: ndarray(int)
ind_members=None
# Choose which longitude should be ploted
# type: ndarray(int)
ind_long=np.array([0])
# Choose which latitude should be ploted
# type: ndarray(int)
ind_lat=np.array([0])

to_standardize = False

# Choose which files should be used
LIST_FILENAMES = listdir(PATH_DATA)
LIST_FILENAMES = [
    fname for fname in LIST_FILENAMES
    if fname.startswith("ec.ens.") and  fname.endswith(".nc")
]
for filename in LIST_FILENAMES:

    list_var, list_names, time = preprocess_data(
        filename = filename,
        path_data = PATH_DATA,
        var_names = var_names,
        ind_time = ind_time,
        ind_members = ind_members,
        ind_long = ind_long,
        ind_lat = ind_lat,
        to_standardize = to_standardize,
        )

    fig_suptitle = "Bergen Forecast: " + filename[:-3] + "\n First grid point, All members"
    list_ax_titles = ["Variable: " + name for name in list_names]
    xlabel = "Time (h)"

    if to_standardize:
        ylabel = "Standardized values (1)"
    else:
        ylabel = ""

    dict_kwargs = {
        "fig_suptitle" : fig_suptitle,
        "list_ax_titles" : list_ax_titles,
        "list_xlabels" : xlabel,
        "list_ylabels" : ylabel,
    }

    fig, axs = from_list_to_subplots(
        list_yvalues=list_var,  # List[ndarray([n_lines, ] n_values )]
        list_xvalues=time, #ndarray(n_values)
        plt_type = "plot",
        dict_kwargs = dict_kwargs,
        show=False,
        )

    name_fig = PATH_FIG+ filename[:-3] + ".png"
    makedirs(PATH_FIG, exist_ok = True)
    plt.savefig(name_fig)
    plt.close()