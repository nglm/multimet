#!/usr/bin/env python3
from os import listdir, makedirs
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import datetime
from netCDF4 import Dataset

from ...PersistentGraph import PersistentGraph
from ...PersistentGraph.plots import *
from ...utils.nc import print_nc_dict
from ...utils.plt import from_list_to_subplots



# ---------------------------------------------------------
# Parameters
# ---------------------------------------------------------

SCORE_TYPES = [
    'inertia',
    'mean_inertia',
    #'weighted_inertia',
    'max_inertia',
    #'min_inertia',       # Shouldn't be used: taking min makes no sense
    # ----------
    'variance',
    'mean_variance',
    #'weighted_variance', # Shouldn't be used: favors very high k values
    #'min_variance',      # Shouldn't be used: taking min makes no sense
    'max_variance',
    # ----------
    #'diameter',      # WARNING: diameter should be used with weights
    #'max_diameter',  # WARNING: Max diameter should be used with weights
    # ----------
    'MedDevMean',
    'mean_MedDevMean',
    'max_MedDevMean',
    # ----------
    #'max_MedDevMed', # Shouldn't be used: see details below
]

# Absolute path to the files
# type: str
PATH_DATA = "/home/natacha/Documents/Work/Data/MLVis2021/"

# Choose the path where the figs will be saved
# type: str
PATH_FIG_PARENT = (
    "/home/natacha/Documents/tmp/figs/PG/MLVis/"
)

MEAN_LW = 2
MEAN_COLOR = 'grey'
MEAN_LS = "-"
MEAN_LABEL = 'mean'
MEAN_ZORDER = 100

STD_LW = 1.5
STD_COLOR = 'grey'
STD_LS = "--"
STD_LABEL = "std"
STD_ZORDER = 100

LW = 0.6
COLOR = 'lightgrey'

OBS_LW = 1.5
OBS_COLOR = 'green'
OBS_LABEL = "obs"
OBS_ZORDER = 99

CTRL_LW = 1.2
CTRL_COLOR = 'orange'
CTRL_LABEL = "ctrl"
CTRL_ZORDER = 98


def preprocess_MLVis_data(verbose = False):
    # Find files
    files = [
        fname for fname in listdir(PATH_DATA)
    ]
    start_date = datetime.datetime(1900,1,1,0)

    # Root dictionary
    data = {}
    # subdictionary names
    dic_names = ['Lothar', 'Sandy', 'heatwave', 'coldwave']
    years = ['1999' , '2012', '2019', '2021']
    f_startswith = ['ec.ens.' + y for y in years]
    ctrl_startswith = ['ec.ensctrl.' + y for y in years]
    obs_startswith = ['e5.ans.' + y for y in years[:-1]] + ['od.ans.2021']
    vars = [['u10', 'v10'], ['msl'], ['t2m'], ['t2m']]
    var_name = ['ff10', 'msl', 't2m', 't2m']
    long_name = []

    for i, name in enumerate(dic_names):
        # New dic for each weather event
        d = {}
        # Meteogram names associated with this weather event
        d['names'] = sorted([f for f in files if f.startswith(f_startswith[i])])
        d['obs_name'] = sorted([
            f for f in files if f.startswith(obs_startswith[i])
        ])[0] #There's just one file
        d['ctrl_names'] = sorted([
            f for f in files if f.startswith(ctrl_startswith[i])
        ])

        # nc files associated with this weather event
        d['nc'] = [Dataset(PATH_DATA + f,'r') for f in d['names']]
        d['obs_nc'] = Dataset(PATH_DATA + d['obs_name'],'r')
        d['ctrl_nc'] = [Dataset(PATH_DATA + f,'r') for f in d['ctrl_names']]

        if verbose:
            # Show what is inside these meteograms
            print(" ----------------------- %s ----------------------- " %name)
            print(" ==== FORECAST ==== ")
            print_nc_dict(d['nc'][0])
            print(" ==== CONTROL ==== ")
            print_nc_dict(d['ctrl_nc'][0])
            print(" ==== OBSERVATION ==== ")
            print_nc_dict(d['obs_nc'])

        # short name for each variable of interest
        d['var_name'] = var_name[i]
        # long name (as defined by the nc file)
        d['long_name'] = d['nc'][0].variables[vars[i][0]].long_name
        # units (as defined by the nc file)
        d['units'] = d['nc'][0].variables[vars[i][0]].units
        # time axis
        d['time'] = [np.array(nc.variables["time"])  for nc in d['nc'] ]
        d['dates'] = [np.array(
            [
                datetime.timedelta(hours=int(t)) + start_date
                for t in nc.variables["time"]
            ]) for nc in d['nc']
        ]
        d['ctrl_time'] = [
            np.array(nc.variables["time"]) for nc in d['ctrl_nc']
        ]
        d['ctrl_dates'] = [np.array(
            [
                datetime.timedelta(hours=int(t)) + start_date
                for t in nc.variables["time"]
            ]) for nc in d['ctrl_nc']
        ]
        d['obs_time'] = np.array(d['obs_nc'].variables["time"])
        d['obs_dates'] = np.array(
            [
                datetime.timedelta(hours=int(t)) + start_date
                for t in d['obs_nc'].variables["time"]
            ])



        # For each nc, create a list of np arrays containing the variable
        # of interest corresponding to the weather event
        var = [
            [ np.array(nc.variables[v]).squeeze() for v in vars[i] ]
            for nc in d['nc']
        ]
        obs_var = [
            np.array(d['obs_nc'].variables[v]).squeeze() for v in vars[i]
        ]
        ctrl_var = [
            [np.array(nc.variables[v]).squeeze() for v in vars[i]]
            for nc in d['ctrl_nc']
        ]

        # Remove missing values
        if name == 'Lothar':
            # Remove missing values
            idx = np.array(
                [bool(i % 2 == 0) for i in range(len(d['time'][0])) ]
            )
            var = [ [ v[idx] for v in v_nc ] for v_nc in var ]
            ctrl_var = [[ v[idx] for v in v_nc ] for v_nc in ctrl_var ]
            d['time'] = [time_nc[idx] for time_nc in d['time'] ]
            d['dates'] = [dates_nc[idx] for dates_nc in d['dates'] ]
            d['ctrl_time'] = [time_nc[idx] for time_nc in d['ctrl_time'] ]
            d['ctrl_dates'] = [dates_nc[idx] for dates_nc in d['ctrl_dates'] ]

        if var_name[i] == 'ff10':
            var = [ [np.sqrt(v_nc[0]**2 + v_nc[1]**2)] for v_nc in var]
            obs_var = [np.sqrt(obs_var[0]**2 + obs_var[1]**2)]
            ctrl_var = [
                [np.sqrt(v_nc[0]**2 + v_nc[1]**2)]
                for v_nc in ctrl_var
            ]
            d['long_name'] = 'wind speed'

        # Now var is simply a list of np arrays(N, T)
        var = [np.swapaxes(v_nc[0], 0,1) for v_nc in var]
        d['var'] = var
        d['obs_var'] = obs_var[0]
        d['ctrl_var'] = [v_nc[0] for v_nc in ctrl_var]


        # add this weather event to our root dictionary
        data[name] = d

    return data

def find_common_dates(t, t_obs, is_Lothar=False):
    # Assume that they are sorted
    start_i_obs = 0
    start_i = 0
    n = len(t)
    n_obs = len(t_obs)
    if t[0] < t_obs[0]:
        for i in range(n):
            if t[i] == t_obs[0]:
                start_i = i
                break
    if t[start_i] > t_obs[0]:
        start_i = 0
        for i in range(n_obs):
            if t[0] <= t_obs[i]:
                start_i_obs = i
                break
    i_obs = []
    i = 0
    while len(i_obs) < n:
        if not is_Lothar:
            if t[i+start_i] == t_obs[i+start_i_obs]:
                i_obs.append(i+start_i_obs)
        else:
            if t[i//2+start_i] == t_obs[i+start_i_obs]:
                i_obs.append(i+start_i_obs)
        i += 1
    return i_obs

def add_fake_legend(
    l = []
):
    lines = []
    labels = []
    if 'mean' in l:
        lines.append()
    colors = ['black', 'red', 'green']
    lines = [Line2D([0], [0], color='grey', linewidth=3, linestyle='--') for c in colors]
    labels = ['black data', 'red data', 'green data']
    plt.legend(lines, labels)


def add_obs(obs_var, obs_time, ax):
    obs_line, = ax.plot(
        obs_time,
        obs_var,
        c=OBS_COLOR, zorder=OBS_ZORDER, lw=OBS_LW,
        label=OBS_LABEL,
    )
    return ax

def add_ctrl(ctrl_var, dates, ax):
    ctrl_line, = ax.plot(
        dates,
        ctrl_var,
        c=CTRL_COLOR, zorder=CTRL_ZORDER, lw=CTRL_LW,
        label=CTRL_LABEL,
    )
    return ax

def add_spaghetti(
    time_axis,
    var,
    ax,
):
    for m in var:
        ax.plot(time_axis, m, lw=LW, color=COLOR)
    mean = np.mean(var, axis = 0)
    std = np.std(var, axis = 0)
    ax.plot(
        time_axis, mean,
        label = MEAN_LABEL, color=MEAN_COLOR,
        lw=MEAN_LW, ls=MEAN_LS, zorder=MEAN_ZORDER
        )
    ax.plot(
        time_axis, mean+std,
        label = STD_LABEL, color=STD_COLOR,
        lw=STD_LW, ls=STD_LS, zorder=STD_ZORDER
    )
    ax.plot(
        time_axis, mean-std,
        color=STD_COLOR,
        lw=STD_LW, ls=STD_LS, zorder=STD_ZORDER
    )
    return ax

def plot_spaghetti(
    show_obs=True,
    show_ctrl=True,
):
    data = preprocess_MLVis_data()
    for name, d in data.items():
        for i in range(len(d['nc'])):

            common_t = find_common_dates(d['time'][i], d['obs_time'])
            fig, ax = plt.subplots(figsize=(15,10))

            # add spaghetti
            ax = add_spaghetti(
                time_axis = d['time'][i],
                var = d['var'][i],
                ax=ax,
            )

            # add obs
            if show_obs:
                ax = add_obs(
                    obs_var=d['obs_var'][common_t],
                    obs_time=d['obs_dates'][common_t],
                    ax=ax
                )
            if show_ctrl:
            # add control member
                ax = add_ctrl(
                    ctrl_var=d['ctrl_var'][i],
                    dates=d['ctrl_dates'][i],
                    ax=ax
                )
            ax.legend()


            title = name + "\n" + d['names'][i]
            ax.set_title(title)
            ax.set_xlabel('')
            ax.set_ylabel(d['long_name'] + ' ('+d['units']+')')
            ax.xaxis.set_major_formatter(mdates.DateFormatter('%m-%d'))
            fig.autofmt_xdate()
            plt.savefig(
                PATH_FIG_PARENT + name +'_'
                + d['names'][i][:-3] + "_" + d['var_name']
                +'.png'
            )


def plot_obs():
    data = preprocess_MLVis_data()
    for name, d in data.items():
        fig, ax = plt.subplots(figsize=(15,10))
        ax.plot(d['obs_time'], d['obs_var'])
        title = name + "\n" + d['obs_name']
        ax.set_title(title)
        ax.set_xlabel('Date')
        ax.set_ylabel(d['long_name'] + ' ('+d['units']+')')
        plt.savefig(
            PATH_FIG_PARENT + name +'_'+ d['obs_name'][:-3]+'.png'
        )

def select_best_examples():
    data = preprocess_MLVis_data()
    best = [
        'ec.ens.1999122512.sfc.meteogram.nc', # Lothar
        'ec.ens.2012102500.sfc.meteogram.nc', # Sandy
        'ec.ens.2019072100.sfc.meteogram.nc', # Heatwave
        'ec.ens.2021020800.sfc.meteogram.nc', # Coldwave
        ]
    max_dates = [
        datetime.datetime(1999, 12, 29, 12), # Lothar
        datetime.datetime(2012, 11,  1, 18), # Sandy
        datetime.datetime(2019,  7, 30, 12), # Heatwave
        datetime.datetime(2021,  2, 17,  0), # Coldwave
    ]
    names = ['Lothar', 'Sandy', 'heatwave', 'coldwave']
    idx = [
        data[names[i]]['names'].index(best[i]) for i in range(len(names))
    ]
    max_t = [
        list(data[names[i]]['dates'][idx[i]]).index(max_dates[i])
        for i in range(len(names))
    ]


    # --------------------------------------------
    # ----- Prepare folders and paths ------------
    # --------------------------------------------
    path_root = PATH_FIG_PARENT + 'best/'
    path_fig = path_root + "plots/"
    path_graph = path_root + "graphs/"
    makedirs(path_fig, exist_ok = True)
    makedirs(path_graph, exist_ok = True)
    FIG_SIZE = (25, 10)

    # ================================
    # Lothar
    # ================================

    k = 0
    i = idx[k]
    name = names[k]
    max_date = max_dates[k]
    d = data[name]
    score = "inertia"
    filename = d['names'][i]
    name_fig = (
        path_fig + name +'_'
        + filename[:-3] + "_" + d['var_name'] +"_"+score
    )
    name_graph = path_graph + filename[:-3] + '.pg'

    fig = plt.figure(figsize = FIG_SIZE, tight_layout=True)
    n = 12
    m = 24
    gs = fig.add_gridspec(nrows=n, ncols=m)

    # ---------------------------
    # Construct graph
    # ---------------------------

    g = PersistentGraph(
            time_axis = d['time'][i][:max_t[k]],
            members = d['var'][i][:, :max_t[k]],
            score_type = score,
            zero_type = 'bounds',
            model_type = 'KMeans',
            k_max = 10,
    )
    g.construct_graph(
        verbose = False,
        quiet = True,
    )
    # ---------------------------------
    # Plots
    # ---------------------------------
    common_t = find_common_dates(
        d['time'][i][:max_t[k]], d['obs_time'], is_Lothar=True,
    )


    # ---- Plot Graph ----
    ax0 = fig.add_subplot(gs[:, 0:m//3])
    _, ax0 = plot_as_graph(
        g, show_vertices=True, show_edges=True,ax=ax0,
        show_std=True)
    ax0.set_title("Entire graph")
    ax0.set_xlabel(' ')
    ax0.set_ylabel(d['long_name'] + ' ('+d['units']+')')
    ax0 = use_dates_as_xticks(ax0,  d['time'][i][:max_t[k]], freq = 1)
    #ax0 = annot_ax(g, ax=ax0)

    # ---- k_plot ----
    # ax1 = fig.add_subplot(gs[5:-1, 1:7], sharex=ax0)
    # _, ax1, _ = k_plot(g, k_max = 5, ax=ax1)
    # #ax1.set_xlabel("Time")
    # ax1.set_ylabel("Relevance")
    # ax1.set_xlabel("")
    # ax1.set_title('Number of clusters: relevance')
    # ax1 = use_dates_as_xticks(ax1,  d['time'][i][:max_t[k]], freq=8)
    # ax1.legend()

    # ---- Spaghetti ----
    ax2 = fig.add_subplot(gs[:, m//3:2*m//3])
    ax2 = add_spaghetti(
        time_axis = d['time'][i][:max_t[k]],
        var = d['var'][i][:, :max_t[k]],
        ax=ax2,
    )

    ax2 = add_obs(
        d['obs_var'][common_t],
        d['obs_time'][common_t],
        ax=ax2,
    )

    ax2 = use_dates_as_xticks(ax2,  d['time'][i][:max_t[k]], freq = 1)
    # We can not really share without that if they have been created
    # separately
    ax0.get_shared_y_axes().join(ax0, ax2)
    # Turn off ticks on this one
    ax2.set_yticklabels([])
    ax2.legend()

    # ---- Most relevant ----
    relevant_k = get_relevant_k(g)
    relevant_k[-3:-2] = [[2, 0] for _ in range(len(relevant_k[-3:-2]))]
    relevant_components = get_relevant_components(g, relevant_k)
    ax3 = fig.add_subplot(gs[:, 2*m//3:])
    _, ax3 = plot_most_revelant_components(
        g, relevant_components=relevant_components,
        show_vertices=True, show_edges=True,ax=ax3,
        show_std=True)
    ax3.set_title("Entire graph")
    ax3.set_xlabel(' ')
    ax3.set_ylabel(d['long_name'] + ' ('+d['units']+')')

    ax3 = add_obs(
        d['obs_var'][common_t],
        d['obs_time'][common_t],
        ax=ax3,
    )

    ax3 = use_dates_as_xticks(ax3,  d['time'][i][:max_t[k]], freq = 1)

    # We can not really share without that if they have been created
    # separately
    ax0.get_shared_y_axes().join(ax0, ax3)
    # Turn off ticks on this one
    ax3.set_yticklabels([])

    fig_suptitle = filename + "\n" + d['var_name']
    fig.suptitle(fig_suptitle)


    # ---------------------------
    # Save plot and graph
    # ---------------------------.
    name_fig += '.png'
    fig.savefig(name_fig)
    plt.close()
    g.save(name_graph)



    # ================================
    # Sandy
    # ================================
    k = 1
    i = idx[k]
    name = names[k]
    max_date = max_dates[k]
    d = data[name]
    score = "inertia"
    filename = d['names'][i]
    name_fig = (
        path_fig + name +'_'
        + filename[:-3] + "_" + d['var_name'] +"_"+score
    )
    name_graph = path_graph + filename[:-3] + '.pg'

    fig = plt.figure(figsize = FIG_SIZE, tight_layout=True)
    gs = fig.add_gridspec(nrows=12, ncols=24)

    # ---------------------------
    # Construct graph
    # ---------------------------

    g = PersistentGraph(
            time_axis = d['time'][i][:max_t[k]],
            members = d['var'][i][:, :max_t[k]],
            score_type = score,
            zero_type = 'bounds',
            model_type = 'KMeans',
            k_max = 10,
    )
    g.construct_graph(
        verbose = False,
        quiet = True,
    )
    # ---------------------------------
    # Plots
    # ---------------------------------

    # ---- Plot Graph ----
    ax0 = fig.add_subplot(gs[:, 0:12])
    _, ax0 = plot_most_revelant_components(
        g, show_vertices=True, show_edges=True,ax=ax0,
        show_std=True)
    ax0.set_title("Entire graph")
    ax0.set_xlabel(' ')
    ax0.set_ylabel(d['long_name'] + ' ('+d['units']+')')
    ax0 = use_dates_as_xticks(ax0,  d['time'][i][:max_t[k]])
    #ax0 = annot_ax(g, ax=ax0)

    # ---- k_plot ----
    ax1 = fig.add_subplot(gs[5:-1, 1:7], sharex=ax0)
    _, ax1, _ = k_plot(g, k_max = 5, ax=ax1)
    #ax1.set_xlabel("Time")
    ax1.set_ylabel("Relevance")
    ax1.set_xlabel("")
    ax1.set_title('Number of clusters: relevance')
    ax1 = use_dates_as_xticks(ax1,  d['time'][i][:max_t[k]], freq=8)
    ax1.legend()

    # ---- Spaghetti ----
    ax2 = fig.add_subplot(gs[:, 12:], sharex=ax0)
    ax2 = add_spaghetti(
        time_axis = d['time'][i][:max_t[k]],
        var = d['var'][i][:, :max_t[k]],
        ax=ax2,
    )
    ax2 = add_ctrl(
        ctrl_var=d['ctrl_var'][i][:max_t[k]],
        dates=d['ctrl_time'][i][:max_t[k]],
        ax=ax2,
    )
    ax2 = use_dates_as_xticks(ax2,  d['time'][i][:max_t[k]])
    # We can not really share without that if they have been created
    # separately
    ax0.get_shared_y_axes().join(ax0, ax2)
    # Turn off ticks on this one
    ax2.set_yticklabels([])
    ax2.legend()

    fig_suptitle = filename + "\n" + d['var_name']
    fig.suptitle(fig_suptitle)


    # ---------------------------
    # Save plot and graph
    # ---------------------------.
    name_fig += '.png'
    fig.savefig(name_fig)
    plt.close()
    g.save(name_graph)


    # ================================
    # Heatwave
    # ================================
    k = 2
    i = idx[k]
    name = names[k]
    max_date = max_dates[k]
    d = data[name]
    score = "inertia"
    filename = d['names'][i]
    name_fig = (
        path_fig + name +'_'
        + filename[:-3] + "_" + d['var_name'] +"_"+score
    )
    name_graph = path_graph + filename[:-3] + '.pg'

    fig = plt.figure(figsize = FIG_SIZE, tight_layout=True)
    n, m = 5, 40
    gs = fig.add_gridspec(nrows=n, ncols=m)

    # ---------------------------
    # Construct graph
    # ---------------------------
    g = PersistentGraph(
            time_axis = d['time'][i][:max_t[k]],
            members = d['var'][i][:, :max_t[k]],
            score_type = score,
            zero_type = 'bounds',
            model_type = 'KMeans',
            k_max = 10,
    )
    g.construct_graph(
        verbose = False,
        quiet = True,
    )
    # ---------------------------------
    # Plots
    # ---------------------------------
    common_t = find_common_dates(d['time'][i][:max_t[k]], d['obs_time'])

    # ---- Plot Graph ----
    ax0 = fig.add_subplot(gs[:, 0:m//2])
    _, ax0 = plot_as_graph(
        g, show_vertices=True, show_edges=True,ax=ax0,
        show_std=True)
    ax0.set_title("Entire graph")
    ax0.set_xlabel(' ')
    ax0.set_ylabel(d['long_name'] + ' ('+d['units']+')')
    ax0 = use_dates_as_xticks(ax0,  d['time'][i][:max_t[k]])
    ax0 = annot_ax(g, ax=ax0)

    # ax0 = add_obs(
    #     d['obs_var'][common_t],
    #     d['obs_time'][common_t],
    #     ax=ax0,
    # )

    # # ---- k_plot ----
    ax1 = fig.add_subplot(gs[:2, 1:9])
    _, ax1, _ = k_plot(g, k_max = 5, ax=ax1)
    ax1.set_ylabel("Relevance")
    ax1.set_xlabel("")

    #  ------------------------- Title inside --------------------------
    ax1.annotate('Number of clusters: relevance',  # Your string

                # The point that we'll place the text in relation to
                xy=(0.17, 0.92),
                # Interpret the x as axes coords, and the y as figure coords
                #xycoords=('axes fraction', 'figure fraction'),
                xycoords=('axes fraction', 'axes fraction'),

                # The distance from the point that the text will be at
                xytext=(0, 0),
                # Interpret `xytext` as an offset in points...
                textcoords='offset points',

                # Any other text parameters we'd like
                #size=14, ha='center', va='bottom')
    )
    #  -----------------------------------------------------------------
    ax1 = use_dates_as_xticks(ax1,  d['time'][i][:max_t[k]], freq=8)
    ax1.legend()

    # ---- Spaghetti ----
    ax2 = fig.add_subplot(gs[:, m//2:], sharex=ax0)
    ax2 = add_spaghetti(
        time_axis = d['time'][i][:max_t[k]],
        var = d['var'][i][:, :max_t[k]],
        ax=ax2,
    )

    # ax2 = add_obs(
    #     d['obs_var'][common_t],
    #     d['obs_time'][common_t],
    #     ax=ax2,
    # )


    ax2 = use_dates_as_xticks(ax2,  d['time'][i][:max_t[k]])
    # We can not really share without that if they have been created
    # separately
    ax0.get_shared_y_axes().join(ax0, ax2)
    # Turn off ticks on this one
    ax2.set_yticklabels([])
    ax2.legend()

    fig_suptitle = filename + "\n" + d['var_name']
    fig.suptitle(fig_suptitle)


    # ---------------------------
    # Save plot and graph
    # ---------------------------.
    name_fig += '.png'
    fig.savefig(name_fig)
    plt.close()
    g.save(name_graph)

def use_dates_as_xticks(
    ax,
    time_axis,
    start_date = datetime.datetime(1900,1,1,0),
    freq = 4
):
    # If you want to have dates as xticks  indpt of what you used to plot your curve
    # uniformly spaced hours between the min and max
    total_hours = np.arange(
        start=time_axis[0], stop=time_axis[-1], step=time_axis[1]-time_axis[0]
    )
    # Now choose how often you want it displayed
    idx = [i for i in range(len(total_hours)) if i%freq==0]
    kept_hours = total_hours[idx]

    # Create the string of dates at the kept locations
    # Creating string here directly is the safest way of
    # controling the format in the plot......
    # Dealing with ax.xaxis.set_major_formatter
    # And ax.xaxis.set_minor_formatter is way too painful...
    labels = [
        (datetime.timedelta(
            hours=int(h)
        ) + start_date).strftime('%m-%d') for h in kept_hours]
    # Specify where you want the xticks
    ax.set_xticks(kept_hours)
    # Specify what you want as xtick labels
    ax.set_xticklabels(labels)
    # The only solution working if you want to change just one ax
    for tick in ax.get_xticklabels():
        tick.set_rotation(30)
    return ax

def main(show_obs=True):

    # ---------------------------
    # Load and preprocess data
    # ---------------------------
    #plt.rcParams.update({'font.size': 30})

    data = preprocess_MLVis_data()
    weights_range = [False]
    for weights in weights_range:
        for score in SCORE_TYPES:
            for pg_type in ['Naive', 'KMeans']:
                path_root = (
                    PATH_FIG_PARENT
                    + pg_type + '/'
                    + score + '/'
                )
                for name, d in data.items():
                    for i in range(len(d['nc'])):

                        filename = d['names'][i]

                        # --------------------------------------------
                        # ----- Prepare folders and paths ------------
                        # --------------------------------------------

                        path_fig = path_root + "plots/"
                        name_fig = (
                            path_fig + name +'_'
                            + filename[:-3] + "_" + d['var_name']
                        )
                        makedirs(path_fig, exist_ok = True)

                        path_graph = path_root + "graphs/"
                        makedirs(path_graph, exist_ok = True)
                        name_graph = path_graph + filename[:-3]

                        # ---------------------------
                        # Construct graph
                        # ---------------------------

                        g = PersistentGraph(
                                time_axis = d['time'][i],
                                members = d['var'][i],
                                score_type = score,
                                zero_type = 'bounds',
                                model_type = pg_type,
                                k_max = 10,
                        )
                        g.construct_graph(
                            verbose = False,
                            quiet = False,
                        )

                        # ---------------------------------
                        # Plot entire graph (with k_plot)
                        # ---------------------------------

                        ax0 = None
                        fig0 = None

                        ax_kw = { }
                        fig_suptitle = filename + "\n" + d['var_name']


                        fig0, ax0 = plot_overview(
                            g, k_max=8, show_vertices=True, show_edges=True,
                            show_std = True, ax_kw=ax_kw, ax = ax0, fig=fig0,
                        )
                        name_fig += '_overview'

                        for ax in ax0:
                            ax = use_dates_as_xticks(ax,  d['time'][i])
                        ax0.set_xlabel(' ')
                        ax0[0].set_ylabel(d['long_name'] + ' ('+d['units']+')')
                        ax0[-1].set_ylabel(d['long_name'] + ' ('+d['units']+')')

                        fig0.suptitle(fig_suptitle)


                        # ---------------------------
                        # Save plot and graph
                        # ---------------------------.
                        name_fig += '.png'
                        fig0.savefig(name_fig)
                        plt.close()
                        g.save(name_graph)

if __name__ == "__main__":
    #preprocess_MLVis_data()
    main()
