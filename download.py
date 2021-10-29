#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from typing import DefaultDict, TextIO
import numpy as np
import zipfile
import requests
from bs4 import BeautifulSoup
import re
import os
import csv
from io import TextIOWrapper
import gzip
import pickle


class DataDownloader:
    """ TODO: dokumentacni retezce

    Attributes:
        headers    Nazvy hlavicek jednotlivych CSV souboru, tyto nazvy nemente!
        regions     Dictionary s nazvy kraju : nazev csv souboru
    """

    headers = ["p1", "p36", "p37", "p2a", "weekday(p2a)", "p2b", "p6", "p7", "p8", "p9", "p10", "p11", "p12", "p13a",
               "p13b", "p13c", "p14", "p15", "p16", "p17", "p18", "p19", "p20", "p21", "p22", "p23", "p24", "p27", "p28",
               "p34", "p35", "p39", "p44", "p45a", "p47", "p48a", "p49", "p50a", "p50b", "p51", "p52", "p53", "p55a",
               "p57", "p58", "a", "b", "d", "e", "f", "g", "h", "i", "j", "k", "l", "n", "o", "p", "q", "r", "s", "t", "p5a"]

    regions = {
        "PHA": "00",
        "STC": "01",
        "JHC": "02",
        "PLK": "03",
        "ULK": "04",
        "HKK": "05",
        "JHM": "06",
        "MSK": "07",
        "OLK": "14",
        "ZLK": "15",
        "VYS": "16",
        "PAK": "17",
        "LBK": "18",
        "KVK": "19",
    }

    def __init__(self, url="https://ehw.fit.vutbr.cz/izv/", folder="data", cache_filename="data_{}.pkl.gz"):
        self.url = url
        self.folder = folder
        self.cache_filename = cache_filename
        self.data = dict()

    def download_data(self):
        # create dir for data
        if not os.path.exists(self.folder):
            os.makedirs(self.folder)

        # get html
        soup = BeautifulSoup(requests.get(self.url).text, "html.parser")
        p = re.compile("(" + self.folder + "/.*\.zip)")

        # get all buttons with text "ZIP" & extract file paths from onclick calls
        file_list = [
            p.search(obj.get("onclick")).group(1)
            for obj in soup.find_all(class_="btn", string="ZIP")
        ]

        # filter files containing data for whole years
        p = re.compile(r".*(?<!\d-)\d{4}\.zip")
        files = list(filter(p.match, file_list))

        # append latest month of latest year
        p = re.compile(r"(\d{2})[-](\d{4}).zip")
        dates = [(y.group(2), y.group(1)) for y in [p.search(f)
                                                    for f in file_list] if y is not None]
        dates.sort()
        date = dates[-1][1] + "-" + dates[-1][0]
        files.append([s for s in file_list if date in s][0])

        # download data & save to specified dir
        for filename in files:
            with requests.get(self.url + "/" + filename) as r:
                with open(filename, "wb") as fp:
                    for chunk in r.iter_content(chunk_size=128, decode_unicode=True):
                        fp.write(chunk)


    def parse_region_data(self, region):
        # check for data files
        if not os.path.isdir(self.folder) or not os.listdir(self.folder):
            self.download_data()

        data = []
        reg = self.regions[region] + ".csv"
        files = os.listdir(self.folder)

        # get files from each year
        p = re.compile(r".*(?<=\d{4})\.zip")
        files = list(filter(p.match, files))
        for zfile in files:
            # get files from specified region
            with zipfile.ZipFile(self.folder + "/" + zfile, "r") as zf:
                with zf.open(reg, "r") as f:
                    tmp = list(csv.reader(TextIOWrapper(
                        f, encoding="cp1250"), delimiter=";"))
                    tmp = [tuple(item.replace(",", ".") if item not in [
                        "", "XX", "A:", "B:", "C:", "D:", "E:", "F:", "G:"] else "-1" for item in row) for row in tmp]
                    data += tmp

        dt = np.dtype(
            "int, int, int, datetime64[D], int, int, int, int, int, int, int, int, int, int, int, int, int, int, int, int, int, int, int, int, int, int, int, int, int, int, int, int, int, int, int, int, int, int, int, int, int, int, int, int, int, str, str, float, float, str, str, str, str, str, str, str, str, str, str, str, str, str, str, str"
        )
        # -- convert [list of tuples] to [structured np.array] to get correct types
        # -- convert [structured np.array] to [2D list], to get rid of tuples
        # -- convert [2D list] to [np.array] && transpose it for [dictionary]
        data = np.array((np.array(data, dtype=dt).tolist())).T

        result = dict(zip(self.headers, np.array(data)))
        result["region"] = np.full(shape=[len(data.T)], fill_value=region)

        return result


    def get_dict(self, regions=None):
        # data already in memory
        if self.data:
            pass

        # fetch data
        else:
            self.data = dict()
            if not regions:
                regions = self.regions.keys()

            for reg in regions:
                # check for cached data
                cache_name = self.folder + "/" + self.cache_filename.format(reg)
                is_cached = False
                if os.path.exists(cache_name):
                    try:
                        with gzip.open(cache_name, "rb") as cache:
                            tmp = pickle.load(cache)
                            is_cached = True
                    except:
                        # invalid cache file --> is_cached is set to False
                        pass

                # fetch data from files && save to cache
                if not is_cached:
                    tmp = self.parse_region_data(reg)

                    # create cache & save data
                    with gzip.open(cache_name, "wb") as cache:
                        pickle.dump(tmp, cache)

                # append to memory
                if not self.data:
                    self.data = tmp
                else:
                    self.data = {k: np.concatenate(
                        (self.data[k], tmp[k])) for k in self.data}

        return self.data


if __name__ == "__main__":
    dd = DataDownloader()
    data = dd.get_dict(["STC", "JHC", "PLK"])
    print("\n\n===================================")
    print("    Data contains", len(data["region"]), "entries\n")
    print("    List of attributes:\n\t\t", [key for key in data])
    print("\n     List of regions:\n\t\t", np.unique(data["region"]))
