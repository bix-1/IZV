#!/usr/bin/env python3.9
# coding=utf-8
from matplotlib import pyplot as plt
import pandas as pd
import seaborn as sns
import sys
import os

# TODO:
# vehicle type: ammount of deaths vs chance of fatality


def plot_injuries(df: pd.DataFrame, fig_location: str = None, show_figure: bool = False):
    # get data
    data = df.loc[(df["p44"] < 9) | (df["p44"] == 16),
                  ["p44", "p13a", "p13b", "p13c"]].copy()

    # set vehicle types
    data["p44"] = data["p44"].map(
        dict.fromkeys((0, 1, 2), "motorcycle") |
        dict.fromkeys((3, 4), "car") |
        dict.fromkeys((5, 6, 7), "truck") |
        {8: "bus"} |
        {16: "train"})
    # set column names
    data.rename({"p13a": "Deaths", "p13b": "Severely injured",
                 "p13c": "Slightly injured"}, axis="columns", inplace=True)

    # plot
    fig, axs = plt.subplots(2, 1, figsize=(12, 8),
                            gridspec_kw={'height_ratios': [2, 1]})
    # sns.set_theme()
    # plt.style.use("ggplot")

    # plot by vehicle type
    dt1 = data.groupby(["p44"]).sum().loc[[
        "car", "truck", "motorcycle", "bus", "train"]]
    dt1.plot.bar(ax=axs[0], rot=0,
                 colormap="autumn", title="Seriousness of accident injuries")
    axs[0].set_yscale("log")
    axs[0].xaxis.label.set_visible(False)

    # plot total count
    data.value_counts("p44").plot.bar(ax=axs[1], rot=0, color="#6c17bd", title="Accidents by vehicle type")
    axs[1].set_yscale("log")
    axs[0].xaxis.label.set_visible(False)

    if fig_location:
        fig.savefig(fig_location)
    if show_figure:
        plt.show()


if __name__ == "__main__":
    df = pd.read_pickle("accidents.pkl.gz")
    plot_injuries(df, "injuries.pdf")
