#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import numpy as np
import matplotlib.pyplot as plt

from download import DataDownloader


def plot_stat(data_source,
              fig_location=None,
              show_figure=False):
    print()

    type_strs = ["Žiadna úprava", "Prerušovaná žltá", "Semafor mimo prevádzky",
                 "Dopravné značky", "Prenosné dopravné značky", "Nevyznačená"]

    data, regions = get_data(data_source)



def get_data(src):
    out = []
    regions, counts = np.unique(src["region"], return_counts=1)
    index = 0
    pos = 0
    N = 6
    for c in counts:
        types, sums = np.unique(src["p24"][pos:pos+c], return_counts=1)
        result = [0] * N
        for i in range(len(types)):
            result[types[i]] = sums[i]

        out.append(result)

        pos += c
        index += 1

    return out, regions


# TODO pri spusteni zpracovat argumenty
if __name__ == "__main__":
    # dd = DataDownloader()
    # dd.get_dict(["PHA"])
    # dd.get_dict(["LBK", "KVK"])
    # dd.get_dict()

    plot_stat(data_source=DataDownloader().get_dict())
