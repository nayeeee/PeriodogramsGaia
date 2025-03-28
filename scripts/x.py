# read a file of the light curve in the folder dataset/eclipsing_binary/
import sys 
import os
import pandas as pd
import numpy as np
import pickle
import ray
from functools import partial

sys.path.append("..")

def filter_lists(list1, list2, list3):
    filtered1, filtered2, filtered3 = [], [], []
    for a, b, c in zip(list1, list2, list3):
        # if any of the three values is nan, skip the index
        if a != a or b != b or c != c:
            continue
        filtered1.append(a)
        filtered2.append(b)
        filtered3.append(c)
    return filtered1, filtered2, filtered3

# Leer el CSV
lc = pd.read_pickle('dataset/eclipsing_binary/5277229516350094592/5277229516350094592.pkl')
print(lc.columns)

for band in ["bp"]:
    print(f"variability_flag_{band}_reject: {lc[f'variability_flag_{band}_reject']}")
        # get the mask of the light curve
    mask = lc[f"variability_flag_{band}_reject"] == "false"
    print(f"mask: {mask}")

    # get the time, flux and flux_err of the light curve
    if band == "g":
        time_, flux_, flux_err_ = lc.loc[mask][["g_transit_time", "g_transit_flux", "g_transit_flux_error"]].values.T
    else:
        time_, flux_, flux_err_ = lc.loc[mask][[f"{band}_obs_time", f"{band}_flux", f"{band}_flux_error"]].values.T
    print(f"time_: {time_} flux_: {flux_} flux_err_: {flux_err_}") 
    time, flux, flux_err = filter_lists(time_, flux_, flux_err_)
    print(f"time: {time} flux: {flux} flux_err: {flux_err}")
        








