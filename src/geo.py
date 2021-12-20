#!/usr/bin/python3.9
# coding=utf-8
import pandas as pd
import geopandas
import matplotlib.pyplot as plt
import contextily as ctx
from sklearn.cluster import KMeans
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
    """
    Create GeoDataFrame

    Parameters
    ----------
    df: pandas.DataFrame
        data
    """
    df["date"] = pd.to_datetime(df["p2a"])
    df = df.loc[df["e"].notnull() & df["d"].notnull()]
    return geopandas.GeoDataFrame(df, geometry=geopandas.points_from_xy(df["d"], df["e"]), crs="EPSG:5514")


def plot_geo(gdf: geopandas.GeoDataFrame, fig_location: str = None,
             show_figure: bool = False):
    """
    Plots graphs showing car accident locations in JHM region (2018-20)

    Parameters
    ----------
    gdf: geopandas.GeoDataFrame
        data

    fig_location: string
        location for storing the plotted figure

    show_figure: bool
        show figure after plotting
    """

    # get data & filter by region, year, road type
    data = gdf[(gdf["region"] == "JHM") & (gdf["p36"] <= 1) &
               (gdf["date"].dt.year <= 2020)].to_crs("EPSG:3857")

    # get graph bounds
    _, miny, maxx, maxy = data.total_bounds
    minx = 1750000.0    # one entry was assigned the wrong region

    # create figure
    rows, cols = 3, 2
    fig, axs = plt.subplots(rows, cols, figsize=(15, 10))
    colors = ["tab:red", "tab:blue"]

    for r in range(rows):
        for c in range(cols):
            axs[r, c].set_title("JHM Region: {} ({})".format(
                "highway" if c == 0 else "1st class road", 2018 + r))
            axs[r, c].axis("off")
            axs[r, c].set_xlim(minx, maxx)
            axs[r, c].set_ylim(miny, maxy)

            # plot data
            data[(data["p36"] == c) & (data["date"].dt.year == (2018 + r))
                 ].plot(ax=axs[r, c], markersize=2, color=colors[c])
            # plot background map
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
    """
    Plots graphs showing car accident density by location in JHM region


    Parameters
    ----------
    gdf: geopandas.GeoDataFrame
        data

    fig_location: string
        location for storing the plotted figure

    show_figure: bool
        show figure after plotting
    """

    # get data & filter by region, road type
    gdata = gdf[(gdf["region"] == "JHM") & (
        gdf["p36"] == 1)]["geometry"].to_crs("EPSG:3857")
    gdata.reset_index(drop=True, inplace=True)

    # get sectors by clustering
    points = pd.DataFrame(
        {"x": gdata.centroid.x, "y": gdata.centroid.y})
    kmeans = KMeans(n_clusters=35, random_state=0)
    clusters = pd.Series(kmeans.fit_predict(points), name="sector")

    # create geo data frame
    data = geopandas.GeoDataFrame(
        data=clusters, geometry=gdata, crs="EPSG:3857")
    # add number of accidents for each sector
    data["counts"] = data.groupby(["sector"])["sector"].transform("count")

    # create figure
    _, ax = plt.subplots(figsize=(12, 8))
    ax.set_title("Accidents in JHM region on 1st class roads")
    ax.axis("off")
    # plot data
    data.plot(ax=ax, column="sector", cmap="OrRd", markersize=5, legend=True)
    # plot background map
    ctx.add_basemap(ax, crs=data.crs,
                    source=ctx.providers.Stamen.TonerLite, alpha=1, zoom=10)

    # showing / storing figure
    if fig_location:
        _save_fig(fig_location)
    if show_figure:
        plt.show()


if __name__ == "__main__":
    gdf = make_geo(pd.read_pickle("../data/accidents.pkl.gz"))
    plot_geo(gdf, "geo1.pdf", False)
    plot_cluster(gdf, "geo2.pdf", False)
