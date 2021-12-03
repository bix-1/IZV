#!/usr/bin/env python3.9
# coding=utf-8
import argparse
from matplotlib import pyplot as plt
import pandas as pd
from pandas.core.series import Series
import seaborn as sns
import numpy as np
import os

# muzete pridat libovolnou zakladni knihovnu ci knihovnu predstavenou na prednaskach
# dalsi knihovny pak na dotaz

""" Ukol 1:
načíst soubor nehod, který byl vytvořen z vašich dat. Neznámé integerové hodnoty byly mapovány na -1.

Úkoly:
- vytvořte sloupec date, který bude ve formátu data (berte v potaz pouze datum, tj sloupec p2a)
- vhodné sloupce zmenšete pomocí kategorických datových typů. Měli byste se dostat po 0.5 GB. Neměňte však na kategorický typ region (špatně by se vám pracovalo s figure-level funkcemi)
- implementujte funkci, která vypíše kompletní (hlubkou) velikost všech sloupců v DataFrame v paměti:
orig_size=X MB
new_size=X MB

Poznámka: zobrazujte na 1 desetinné místo (.1f) a počítejte, že 1 MB = 1e6 B.
"""


def print_size(type, df):
    print(type + "_size=" + "{:.1f}".format(
          df.memory_usage(deep=True).sum() / (1024*1024)), "MB")


def get_dataframe(filename: str, verbose: bool = False) -> pd.DataFrame:
    df = pd.read_pickle(filename)
    if verbose:
        print_size("orig", df)

    exclude = ["p1", "d", "e", "region", "p21"]
    reduce_list = list(set(df.columns) - set(exclude))
    for col in reduce_list:
        df[col] = df[col].astype("category")

    df["date"] = pd.to_datetime(df["p2a"])

    if verbose:
        print_size("new", df)
    return df


def plot_roadtype(df: pd.DataFrame, fig_location: str = None,
                  show_figure: bool = False):
    regs = ["VYS", "PAK", "LBK", "KVK"]

    df["p21"] = pd.cut(df["p21"], [-1, 0, 1, 2, 4, 5, 6])
    data = df.loc[df["region"].isin(regs), ["p21", "region"]]

    sns.set_theme()
    g = sns.catplot(data=data, x="region", kind="count",
                    col="p21", col_wrap=3, palette="flare", height=3)
    g.set_axis_labels("Region", "Accidents")
    titles = ["Two-lane road", "Three-lane road", "Four-lane road",
              "Multi-lane road", "Expressway", "Other road"]

    for i in range(6):
        g.axes[i].set_title(titles[i])
        g.axes[i].set_yscale("log")


    # showing / storing figure
    if fig_location:
        plt.savefig(fig_location)
    if show_figure:
        plt.show()


def plot_animals(df: pd.DataFrame, fig_location: str = None,
                 show_figure: bool = False):
    regs = ["STC", "ULK", "JHM", "VYS"]

    # filter by year & cause; get required columns
    df = df.loc[(df["date"].dt.year < 2021) &
                (df["p58"] == 5) &
                (df["region"].isin(regs)), ["region", "p10", "date"]]
    # replace categories
    df["p10"] = df["p10"].map(
        dict.fromkeys((1, 2), "driver") |
        {4: "animal"} |
        dict.fromkeys((-1, 0, 3, 5, 6, 7), "other"))
    # get month from dates
    df["date"] = df["date"].dt.month

    # plotting
    g = sns.catplot(data=df, x="date", hue="p10", col="region", kind="count",
                    hue_order=["animal", "driver", "other"],
                    col_wrap=2, height=3.5, aspect=1.5, sharex=False)
    g.set_ylabels("Accidents")
    g.set_titles("Region: {col_name}")
    for x in g.axes:
        x.set_xlabel("Month")

    # showing / storing figure
    if fig_location:
        plt.savefig(fig_location)
    if show_figure:
        plt.show()


# Ukol 4: Povětrnostní podmínky
def plot_conditions(df: pd.DataFrame, fig_location: str = None,
                    show_figure: bool = False):


    # showing / storing figure
    if fig_location:
        plt.savefig(fig_location)
    if show_figure:
        plt.show()


if __name__ == "__main__":
    df = get_dataframe("accidents.pkl.gz")
    plot_roadtype(df, fig_location="01_roadtype.png", show_figure=True)
    # plot_animals(df, "02_animals.png", True)
    # plot_conditions(df, "03_conditions.png", True)
