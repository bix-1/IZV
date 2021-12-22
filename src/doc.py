#!/usr/bin/env python3.9
# coding=utf-8
from matplotlib import pyplot as plt
import pandas as pd
import seaborn as sns
import sys
import os


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
    plt.style.use("ggplot")
    fig, axs = plt.subplots(2, 1, figsize=(12, 8),
                            gridspec_kw={'height_ratios': [2, 1]})
    for ax in axs:
        ax.xaxis.label.set_visible(False)
    axs[0].set_yscale("log")

    # plot by vehicle type
    dt1 = data.groupby(["p44"]).sum().loc[[
        "car", "truck", "motorcycle", "bus", "train"]]
    dt1.plot.bar(ax=axs[0], rot=0,
                 colormap="autumn", title="Seriousness of injuries")
    axs[0].set_ylabel("accidents")
    axs[0].grid(visible=False, axis="x")

    # plot total count
    plt.style.use("seaborn-dark")
    counts = data.value_counts("p44")
    counts.plot.bar(
        ax=axs[1], rot=0, color="#6c17bd", title="Lives threatened per accident")
    axs[1].set_ylabel("accidents", color="#6c17bd")
    axs[1].tick_params(axis='y', labelcolor="#6c17bd")
    axs[1].grid(True)
    axs[1].yaxis.set_ticks(axs[1].get_yticks())  # FixedLocator warning
    yticks = ['{:.0f}'.format(x) + 'K' for x in axs[1].get_yticks()/1000]
    axs[1].set_yticklabels(yticks)

    # plot probability of injury
    ax3 = axs[1].twinx()
    ax3.set_ylabel("threatened", color="#DC143C")
    ax3.tick_params(axis='y', labelcolor="#DC143C")
    dt2 = (dt1["Deaths"] + dt1["Severely injured"]) / data.value_counts("p44")
    dt2.plot.bar(ax=ax3, color="#DC143C", width=0.2)
    xlocs, _ = plt.xticks()
    for index, value in enumerate(dt2.values.tolist()):
        plt.text(xlocs[index] - 0.12, value + 0.01,
                 "{:,.2f}%".format(value), fontsize=12, fontweight="bold")
    plt.text(xlocs[-1] - 0.25, 0.025, str(counts.at["train"]),
             fontsize=14, fontweight="bold", color="#6c17bd")
    plt.plot([xlocs[-1] - 0.18, xlocs[-1]], [0.018, 0], color="#6c17bd", lw=3)

    # figure storing / showing
    if fig_location:
        fig.savefig(fig_location)
    if show_figure:
        plt.show()


if __name__ == "__main__":
    df = pd.read_pickle("accidents.pkl.gz")
    plot_injuries(df, "injuries.pdf")
