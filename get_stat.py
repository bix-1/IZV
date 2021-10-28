#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import numpy as np
import matplotlib.pyplot as plt
# povolene jsou pouze zakladni knihovny (os, sys) a knihovny numpy, matplotlib a argparse

from download import DataDownloader


def plot_stat(data_source,
              fig_location=None,
              show_figure=False):
    pass


# TODO pri spusteni zpracovat argumenty
if __name__ == "__main__":
    dd = DataDownloader()
    dd.get_dict(["PHA"])
    # dd.get_dict(["LBK", "KVK"])
    # dd.get_dict()


