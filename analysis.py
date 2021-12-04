#!/usr/bin/env python3.9
# coding=utf-8
from datetime import date
from matplotlib import pyplot as plt
import pandas as pd
import seaborn as sns
import matplotlib.dates as mdates
import os
import sys


def _print_size(type, df):
    print(type + "_size=" + "{:.1f}".format(
          df.memory_usage(deep=True).sum() / (1024*1024)), "MB")


def _save_fig(fig_location):
    try:
        dir = os.path.dirname(fig_location)
        if dir and not os.path.exists(dir):
            os.makedirs(dir)
        plt.savefig(fig_location)
    except:
        print("ERROR: Failed to save figure", fig_location, file=sys.stderr)
        sys.exit(1)


def get_dataframe(filename: str, verbose: bool = False) -> pd.DataFrame:
    df = pd.read_pickle(filename)
    if verbose:
        _print_size("orig", df)

    exclude = ["p1", "d", "e", "region", "p21", "p2a"]
    reduce_list = list(set(df.columns) - set(exclude))
    for col in reduce_list:
        df[col] = df[col].astype("category")

    df["date"] = pd.to_datetime(df["p2a"])

    if verbose:
        _print_size("new", df)
    return df


def plot_roadtype(df: pd.DataFrame, fig_location: str = None,
                  show_figure: bool = False):
    regs = ["VYS", "PAK", "LBK", "KVK"]

    df["p21"] = pd.cut(df["p21"], [-1, 0, 1, 2, 4, 5, 6])
    data = df.loc[df["region"].isin(regs), ["p21", "region"]]

    # plotting
    sns.set_theme()
    g = sns.catplot(data=data, x="region", kind="count",
                    col="p21", col_wrap=3, palette="flare", height=3)
    g.set_axis_labels("Region", "Accidents")
    titles = ["Two-lane road", "Three-lane road", "Four-lane road",
              "Multi-lane road", "Expressway", "Other road"]
    for i in range(6):
        g.axes[i].set_title(titles[i])
        g.axes[i].set_yscale("log")
    plt.suptitle("Accidents per road type")
    plt.subplots_adjust(top=0.88)

    # showing / storing figure
    if fig_location:
        _save_fig(fig_location)
    if show_figure:
        plt.show()


def plot_animals(df: pd.DataFrame, fig_location: str = None,
                 show_figure: bool = False):
    regs = ["STC", "ULK", "JHM", "VYS"]

    # filter by year & cause; get required columns
    data = df.loc[(df["date"].dt.year < 2021) &
                  (df["p58"] == 5) &
                  (df["region"].isin(regs)), ["region", "p10", "date"]]
    # replace categories
    data["p10"] = data["p10"].map(
        dict.fromkeys((1, 2), "driver") |
        {4: "animal"} |
        dict.fromkeys((-1, 0, 3, 5, 6, 7), "other"))
    # get month from dates
    data["date"] = data["date"].dt.month

    # plotting
    sns.set_theme()
    g = sns.catplot(data=data, x="date", hue="p10", col="region", kind="count",
                    hue_order=["animal", "driver", "other"], palette="rocket_r",
                    col_wrap=2, height=3.5, aspect=1.5, sharex=False, legend=False)
    g.set_ylabels("Accidents")
    g.set_titles("Region: {col_name}")
    g.add_legend(title="At fault")
    plt.subplots_adjust(hspace=.35)
    for x in g.axes:
        x.set_xlabel("Month")
    plt.suptitle("Accidents involving animals")
    plt.subplots_adjust(top=0.88)

    # showing / storing figure
    if fig_location:
        _save_fig(fig_location)
    if show_figure:
        plt.show()


def plot_conditions(df: pd.DataFrame, fig_location: str = None,
                    show_figure: bool = False):
    regs = ["STC", "ULK", "JHM", "VYS"]

    # filter by wind conds & region; get required columns
    data = df.loc[(df["p18"] != 0) & (df["region"].isin(regs)),
                  ["region", "date", "p18"]]
    # replace values
    data["p18"] = data["p18"].map({
        1: "unobstructed",
        2: "fog",
        3: "weak rain",
        4: "rain",
        5: "snow",
        6: "frosty road",
        7: "wind gust",
    })

    data = pd.pivot_table(
        data, index=["region", "date"], columns="p18", aggfunc="size")
    data = data.unstack("region").resample(
        "M").sum().astype("int").stack("region").reset_index()
    data = pd.melt(data, id_vars=["region", "date"])

    # plotting
    sns.set_theme()
    g = sns.FacetGrid(data, col="region", height=3.5,
                      aspect=1.5, col_wrap=2, sharex=False)
    g.map(sns.lineplot, "date", "value", "p18")
    plt.subplots_adjust(wspace=0.15)
    g.set_ylabels("Accidents")
    g.set_xlabels("")
    g.set_titles("Region: {col_name}")
    g.add_legend(title="Conditions", borderpad=1.5)
    g.set(xlim=(date(2016, 1, 1), date(2021, 1, 1)))
    xformatter = mdates.DateFormatter("%m/%y")
    for ax in g.axes:
        ax.xaxis.set_major_formatter(xformatter)
    plt.suptitle("Accidents per road conditions")
    plt.subplots_adjust(top=0.88)

    # showing / storing figure
    if fig_location:
        _save_fig(fig_location)
    if show_figure:
        plt.show()


if __name__ == "__main__":
    df = get_dataframe("accidents.pkl.gz", verbose=True)
    plot_roadtype(df, "01_roadtype.png")
    plot_animals(df, "02_animals.png")
    plot_conditions(df, "03_conditions.png")
