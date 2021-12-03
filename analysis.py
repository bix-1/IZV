#!/usr/bin/env python3.9
# coding=utf-8
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
    print_size("orig", df)

    exclude = ["p1", "d", "e"]
    reduce_list = list(set(df.columns) - set(exclude))
    for col in reduce_list:
        df[col] = df[col].astype("category")

    df["date"] = pd.to_datetime(df["p2a"])

    print_size("new", df)
    return df

# Ukol 2: počty nehod v jednotlivých regionech podle druhu silnic


def plot_roadtype(df: pd.DataFrame, fig_location: str = None,
                  show_figure: bool = False):
    pass

# Ukol3: zavinění zvěří


def plot_animals(df: pd.DataFrame, fig_location: str = None,
                 show_figure: bool = False):
    pass

# Ukol 4: Povětrnostní podmínky


def plot_conditions(df: pd.DataFrame, fig_location: str = None,
                    show_figure: bool = False):
    pass


if __name__ == "__main__":
    # zde je ukazka pouziti, tuto cast muzete modifikovat podle libosti
    # skript nebude pri testovani pousten primo, ale budou volany konkreni ¨
    # funkce.
    # tento soubor si stahnete sami, při testování pro hodnocení bude existovat
    df = get_dataframe("accidents.pkl.gz")
    exit()
    plot_roadtype(df, fig_location="01_roadtype.png", show_figure=True)
    plot_animals(df, "02_animals.png", True)
    plot_conditions(df, "03_conditions.png", True)
