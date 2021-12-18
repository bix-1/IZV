#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# File: get_start.py
# Brief: Extraction & plotting of data
#
# Project: Data analysis & visualization of traffic accidents
#
# Authors: Jakub Bartko    xbartk07@stud.fit.vutbr.cz


import argparse
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.colors as colors
import os
from download import DataDownloader


def get_data(src):
    """
    Extracts data for later plotting from data source

    Params
    ------
    src: dict
        dictionary representing data entries: {header: np.array(entries)}

    Returns
    -------
    dict
        dictionary of extracted data: {header: np.array(entries)}
    """

    N = 6   # number of accident types
    out = []
    regions = []

    # get boundaries of entries for each region
    indices = np.unique(src["region"], return_index=True)[1].tolist()
    indices.sort()
    indices.append(-1)

    # extract entries for each region
    for i in range(len(indices)-1):
        # get counts of each type of accident
        types, sums = np.unique(
            src["p24"][indices[i]:indices[i+1]], return_counts=True)
        regions.append(src["region"][indices[i]])

        # fix type counts
        # --> correct position & replace missing values with 0
        result = [0] * N
        for j in range(len(types)):
            result[types[j]] = sums[j]
        out.append(result)

    return out, regions


def plot_stat(data_source,
              fig_location=None,
              show_figure=False):
    """
    Plots extracted data as heatmaps visualizing types of accidents for each region.

    Parameters
    ----------
    data_source: dict
        dictionary of data entries: {header: np.array(entries)}
    fig_location: str
        filename for saving of plotted figure
    show_figure: bool
        show plotted figure
    """

    # extract data & list of regions
    data, regions = get_data(data_source)

    type_strs = ["Flashing yellow light", "Traffic light out of order", "Road signs",
                 "Mobile road signs", "Uncontrolled intersection", "No giving way"]
    # shift accident types for prettier graph
    data = np.array(data).T
    data = np.roll(data, -1, axis=0)

    fig = plt.figure(figsize=(9, 7))
    plt.subplots_adjust(left=0.3, hspace=0.35)

    ###########################################################
    # Figure n.1 - counts of accident types per each region
    ax = fig.add_subplot(2, 1, 1)
    ax.set_title("Absolute values")

    ax.set_yticks(np.arange(len(type_strs))+0.5)
    ax.set_yticklabels(type_strs)
    ax.set_xticks(np.arange(len(regions))+0.5)
    ax.set_xticklabels(regions)
    ax.invert_yaxis()

    heatmap = ax.pcolor(data, norm=colors.LogNorm())
    cb = plt.colorbar(heatmap, shrink=1.1)
    cb.set_label("Number of accidents")

    ################################################################
    # Figure n.2 - relative counts of accident types per each region
    sum = data.sum(axis=1)
    norm_data = data * 100 / sum[:, np.newaxis]
    norm_data = np.where(np.isclose(norm_data, 0), np.NaN, norm_data)

    ax = fig.add_subplot(2, 1, 2)
    ax.set_title("Relatively to causes")

    ax.set_yticks(np.arange(len(type_strs))+0.5)
    ax.set_yticklabels(type_strs)
    ax.set_xticks(np.arange(len(regions))+0.5)
    ax.set_xticklabels(regions)
    ax.invert_yaxis()

    heatmap = ax.pcolor(norm_data, cmap="plasma", vmin=0, vmax=100)
    cb = plt.colorbar(heatmap, shrink=1.1)
    cb.set_label("Portion of accidents due to cause [%]")

    ###########################################################
    if fig_location:
        path = os.path.dirname(fig_location)
        if path and not os.path.exists(path):
            os.makedirs(os.path.dirname(fig_location), exist_ok=True)
        plt.savefig(fig_location)
    if show_figure:
        plt.show()


if __name__ == "__main__":
    # parse CL arguments
    aparser = argparse.ArgumentParser(
        description="Fetches, processes & plots data of traffic accidents")
    aparser.add_argument(
        "-f",
        "--fig_location",
        required=False,
        default="",
        help="specify location for saving the plotted graph"
    )
    aparser.add_argument(
        "-s",
        "--show_figure",
        required=False,
        default=False,
        action="store_true",
        help="show figure after plotting"
    )
    args = aparser.parse_args()

    plot_stat(data_source=DataDownloader().get_dict(),
              fig_location=args.fig_location, show_figure=args.show_figure)
