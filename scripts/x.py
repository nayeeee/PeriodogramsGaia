# read a file of the light curve in the folder dataset/eclipsing_binary/
import sys 
import os
import pandas as pd
import numpy as np
import pickle
import ray
from functools import partial
from astropy.timeseries import LombScargle


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

def filter_flux_over_error(flux_over_error, time, mag):
    err = []
    time_filtered = []
    mag_filtered = []
    for i, error in enumerate(flux_over_error):
        if error > 0:
            err.append(error)
            time_filtered.append(time[i])
            mag_filtered.append(mag[i])
    return np.array(err), np.array(time_filtered), np.array(mag_filtered)

# Leer el CSV
# lc = pd.read_pickle('dataset/eclipsing_binary/5277229516350094592/5277229516350094592.pkl')
lc = pd.read_pickle('dataset/eclipsing_binary/2250237892996834304/2250237892996834304.pkl')
print(lc.columns)
grid = pd.read_csv(os.path.join("dataset", "grid.csv"))
min_freq = grid[grid["type"] == "eclipsing_binary"]["low-frequency"].values[0]
max_freq = grid[grid["type"] == "eclipsing_binary"]["high-frequency"].values[0]
freq = np.arange(min_freq, 2*max_freq, 1e-4)

for band in ["g", "bp", "rp"]:
    mask = lc[f"variability_flag_{band}_reject"] == "false" # VERIFY THAT THIS FILTER IS CORRECT
        
    if sum(mask) == 0:
        print(f"No points in {band}")
        continue
        
    # get the time, mag and mag_err of the light curve
    if band == "g":
        time_, mag_, flux_over_error_ = lc.loc[mask][["g_transit_time", "g_transit_mag", "g_transit_flux_over_error"]].values.T
    else:
        time_, mag_, flux_over_error_ = lc.loc[mask][[f"{band}_obs_time", f"{band}_mag", f"{band}_flux_over_error"]].values.T
    
    print(f"band: {band} \n len time_: {len(time_)}, len mag_: {len(mag_)}, len flux_over_error_: {len(flux_over_error_)}")

    time, mag, flux_over_error = filter_flux_over_error(flux_over_error_, time_, mag_)
    # extract the error of the mag from this formula: 2.5/(np.log(10)*flux_over_error)
    err = 2.5/(np.log(10)*flux_over_error)

    print(f"band: {band} \n len time: {len(time)}, len mag: {len(mag)}, len err: {len(err)}")
    
    periodogram = LombScargle(time, mag, err).power(freq)








