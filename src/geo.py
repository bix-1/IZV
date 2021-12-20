#!/usr/bin/python3.9
# coding=utf-8
import pandas as pd
import geopandas
import matplotlib.pyplot as plt
import contextily as ctx
from sklearn.cluster import KMeans
import numpy as np
import sys
import os


def _save_fig(fig_location):
    """
    Saves current PyPlot figure to specified location

    Parameters
    ----------
    fig_location: str
        path for figure storing
    """

    try:
        dir = os.path.dirname(fig_location)
        if dir and not os.path.exists(dir):
            os.makedirs(dir)
        plt.savefig(fig_location)
    except:
        print("ERROR: Failed to save figure", fig_location, file=sys.stderr)
        sys.exit(1)


def make_geo(df: pd.DataFrame) -> geopandas.GeoDataFrame:
    df["date"] = pd.to_datetime(df["p2a"])
    df = df.loc[df["e"].notnull() & df["d"].notnull()]
    return geopandas.GeoDataFrame(df, geometry=geopandas.points_from_xy(df["d"], df["e"]), crs="EPSG:5514")


def plot_geo(gdf: geopandas.GeoDataFrame, fig_location: str = None,
             show_figure: bool = False):
    """ Vykresleni grafu s sesti podgrafy podle lokality nehody
     (dalnice vs prvni trida) pro roky 2018-2020 """

    data = gdf[(gdf["region"] == "JHM") & (gdf["p36"] <= 1) &
              (gdf["date"].dt.year <= 2020)].to_crs("EPSG:3857")

    rows, cols = 3, 2
    fig, axs = plt.subplots(rows, cols, figsize=(15, 10))

    _, miny, maxx, maxy = data.total_bounds
    minx = 1750000.0    # one entry was assigned the wrong region

    colors = ["tab:red", "tab:blue"]

    for r in range(rows):
        for c in range(cols):
            axs[r, c].set_title("JHM Region: {} ({})".format(
                "highway" if c == 0 else "1st class road", 2018 + r))
            axs[r, c].axis("off")
            axs[r, c].set_xlim(minx, maxx)
            axs[r, c].set_ylim(miny, maxy)

            data[(data["p36"] == c) & (data["date"].dt.year == (2018 + r))
                ].plot(ax=axs[r, c], markersize=2, color=colors[c])
            ctx.add_basemap(axs[r, c], crs=data.crs.to_string(), source=ctx.providers.Stamen.TonerLite,
                            alpha=0.9, zoom=10)

    plt.tight_layout()

    # showing / storing figure
    if fig_location:
        _save_fig(fig_location)
    if show_figure:
        plt.show()


def plot_cluster(gdf: geopandas.GeoDataFrame, fig_location: str = None,
                 show_figure: bool = False):
    """ Vykresleni grafu s lokalitou vsech nehod v kraji shlukovanych do clusteru """
    # get geo data
    gdata = gdf[(gdf["region"] == "JHM") & (
        gdf["p36"] == 1)]["geometry"].to_crs("EPSG:3857")
    gdata.reset_index(drop=True, inplace=True)

    # get sector number
    points = pd.DataFrame(
        {"x": gdata.centroid.x, "y": gdata.centroid.y})
    kmeans = KMeans(n_clusters=35, random_state=0)
    clusters = pd.Series(kmeans.fit_predict(points), name="sector")

    data = geopandas.GeoDataFrame(
        data=clusters, geometry=gdata, crs="EPSG:3857")

    data["counts"] = data.groupby(["sector"])["sector"].transform("count")

    figure, ax = plt.subplots(figsize=(12, 8))
    data.plot(ax=ax, column="sector", cmap="OrRd", markersize=5, legend=True)
    ctx.add_basemap(ax, crs=data.crs,
                    source=ctx.providers.Stamen.TonerLite, alpha=1, zoom=10)
    ax.axis("off")
    ax.set_title("Accidents in JHM region on 1st class roads")

    # showing / storing figure
    if fig_location:
        _save_fig(fig_location)
    if show_figure:
        plt.show()


if __name__ == "__main__":
    gdf = make_geo(pd.read_pickle("../data/accidents.pkl.gz"))
    plot_geo(gdf, "geo1.pdf", False)
    plot_cluster(gdf, "geo2.pdf", False)
