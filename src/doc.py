#!/usr/bin/env python3.9
# coding=utf-8
from matplotlib import pyplot as plt
import pandas as pd


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
    fig, axs = plt.subplots(2, 1, figsize=(8, 8),
                            gridspec_kw={'height_ratios': [3, 2]})
    for ax in axs:
        ax.xaxis.label.set_visible(False)
        ax.tick_params(axis="x", labelsize=14)
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
    ax3.tick_params(axis="x", labelsize=14)
    ax3.set_ylabel("threatened", color="#DC143C")
    ax3.tick_params(axis='y', labelcolor="#DC143C")
    dt2 = (dt1["Deaths"] + dt1["Severely injured"]) / data.value_counts("p44")
    dt2.plot.bar(ax=ax3, color="#DC143C", width=0.2)
    xlocs, _ = plt.xticks()
    for index, value in enumerate(dt2.values.tolist()):
        plt.text(xlocs[index] - 0.12, value + 0.01,
                 "{:,.2f}".format(value), fontsize=12, fontweight="bold")
    plt.text(xlocs[-1] - 0.25, 0.025, str(counts.at["train"]),
             fontsize=14, fontweight="bold", color="#6c17bd")
    plt.plot([xlocs[-1] - 0.18, xlocs[-1]], [0.018, 0], color="#6c17bd", lw=3)

    plt.tight_layout()

    # figure storing / showing
    if fig_location:
        fig.savefig(fig_location)
    if show_figure:
        plt.show()


def plot_table(df: pd.DataFrame, out_location: str = None):
    # get data
    data = df.loc[(df["p44"] < 9) | (df["p44"] == 16),
                  ["p44", "p13a", "p13b", "p13c"]].copy()

    # set vehicle types
    data["p44"] = df["p44"].map(
        dict.fromkeys((0, 1, 2), "motorcycle") |
        dict.fromkeys((3, 4), "car") |
        dict.fromkeys((5, 6, 7), "truck") |
        {8: "bus"} |
        {16: "train"})
    # set column names
    data.rename({"p13a": "Deaths", "p13b": "Severely injured",
                 "p13c": "Slightly injured"}, axis="columns", inplace=True)

    # add injury data
    table = pd.DataFrame()
    # n of accidents
    table["Accidents"] = data.value_counts("p44").rename_axis('Vehicles')
    # % of total
    total_acc = table["Accidents"].sum()
    table["Of total acc."] = (
        table["Accidents"] * 100 / total_acc).map("{:.0f}%".format)
    table.at["train", "Of total acc."] = "<1%"
    # % with injury
    data_inj = data.loc[(data["Deaths"] > 0) | (data["Severely injured"] > 0) | (
        data["Slightly injured"] > 0)].value_counts("p44") * 100 / table["Accidents"]
    table["With injury"] = data_inj.map("{:.0f}%".format)
    # total injured
    inj_categories = data.groupby(["p44"]).sum().rename_axis('Vehicles')
    table["Injured"] = inj_categories.sum(axis=1)
    # of total
    total = table["Injured"].sum()
    table["Of total inj."] = (
        table["Injured"] * 100 / total).map("{:.0f}%".format)
    table.at["train", "Of total inj."] = "<1%"
    # by injury category
    table = pd.concat([table, inj_categories], axis=1)
    table["Injured per accident"] = table["Injured"] / table["Accidents"]
    table["Lives threatened per accident"] = (
        table["Deaths"] + table["Severely injured"]) / table["Accidents"]

    pd.set_option("display.max_rows", None, "display.max_columns", None)
    print(table, "\n")
    if out_location:
        table.to_csv(out_location)

    ratio = table.at["bus", "Injured"] / table.at["train", "Injured"]
    print("Trains are responsible for", "{:.0f}x".format(ratio),
          "less injuries than the next safest vehicle - a bus.")

    threats = table["Lives threatened per accident"]
    train_car = threats["train"] / threats["car"]
    car_bike = data_inj["motorcycle"] / data_inj["car"]
    print("An accident involving train is", "{:.0f}x".format(train_car), "times more likely to cause a life threatening injury than a car.")
    print("Accidents caused by motorcycles are", "{:.0f}x".format(car_bike), "times more likely to result in an injury than the ones caused by cars.")


if __name__ == "__main__":
    df = pd.read_pickle("accidents.pkl.gz")
    # plot_injuries(df, "injuries.pdf")
    plot_table(df, "data.csv")
