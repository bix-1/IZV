#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.colors as colors
import os

from download import DataDownloader


def get_data(src):
    N = 6
    out = []
    regions = []
    indices = np.unique(src["region"], return_index=True)[1].tolist()
    indices.sort()
    indices.append(-1)

    for i in range(len(indices)-1):
        types, sums = np.unique(
            src["p24"][indices[i]:indices[i+1]], return_counts=True)
        regions.append(src["region"][indices[i]])

        result = [0] * N
        for j in range(len(types)):
            result[types[j]] = sums[j]
        out.append(result)

    return out, regions


def plot_stat(data_source,
              fig_location=None,
              show_figure=False):

    data, regions = get_data(data_source)

    type_strs = ["Prerušovaná žltá", "Semafor mimo prevádzky", "Dopravné značky",
                 "Prenosné dopravné značky", "Nevyznačená", "Žiadna úprava"]

    data = np.array(data).T
    data = np.roll(data, -1, axis=0)

    fig = plt.figure(figsize=(9, 7))
    plt.subplots_adjust(left=0.3, hspace=0.35)

    ax = fig.add_subplot(2, 1, 1)
    ax.set_title("Absolútne")

    ax.set_yticks(np.arange(len(type_strs))+0.5)
    ax.set_yticklabels(type_strs)
    ax.set_xticks(np.arange(len(regions))+0.5)
    ax.set_xticklabels(regions)
    ax.invert_yaxis()

    heatmap = ax.pcolor(data, norm=colors.LogNorm())
    cb = plt.colorbar(heatmap, shrink=1.1)
    cb.set_label("Počet nehôd")

    ###########################################################
    sum = data.sum(axis=1)
    norm_data = data * 100 / sum[:, np.newaxis]
    norm_data = np.where(np.isclose(norm_data, 0), np.NaN, norm_data)

    ax = fig.add_subplot(2, 1, 2)
    ax.set_title("Relatívne voči príčine")

    ax.set_yticks(np.arange(len(type_strs))+0.5)
    ax.set_yticklabels(type_strs)
    ax.set_xticks(np.arange(len(regions))+0.5)
    ax.set_xticklabels(regions)
    ax.invert_yaxis()

    heatmap = ax.pcolor(norm_data, cmap="plasma", vmin=0, vmax=100)
    cb = plt.colorbar(heatmap, shrink=1.1)
    cb.set_label("Podiel nehôd pre danú príčinu [%]")

    if fig_location:
        path = os.path.dirname(fig_location)
        if path and not os.path.exists(path):
            os.makedirs(os.path.dirname(fig_location), exist_ok=True)
        plt.savefig(fig_location)
    if show_figure:
        plt.show()


# TODO pri spusteni zpracovat argumenty
if __name__ == "__main__":
    plot_stat(data_source=DataDownloader().get_dict(),
              fig_location="plot.png", show_figure=True)
