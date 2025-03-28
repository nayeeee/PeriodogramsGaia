# calculate the periodograms of the light curves
import sys 
import os
import pandas as pd
import numpy as np
import pickle
import ray

from tqdm import tqdm
from functools import partial
from astropy.timeseries import LombScargle
from astropy.timeseries import LombScargleMultiband
from timeit import timeit
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

@ray.remote(num_cpus=4)
def periodograms_band(freq, d_folder_type, folder_lc, dict_per, without_points):
    # path of the light curve
    d_folder_lc = os.path.join(d_folder_type, folder_lc)
    lc = pd.read_pickle(os.path.join(d_folder_lc, folder_lc+'.pkl'))
    # name of the light curve
    name_lc = lc.source_id.iloc[0]
    print(f"Calculating periodograms of {name_lc}")
    # period of the light curve
    # period = valid_lightcurves[valid_lightcurves["source_id"] == name_lc]['pf'].values[0]

    # initialize list of time, flux and flux_err to multiband
    times, fluxes, fluxes_err, bands = [], [], [], []
    # calculate the periodogram for each band and multiband
    for band in ["g", "bp", "rp"]:
        # get the mask of the light curve
        mask = lc[f"variability_flag_{band}_reject"] == "false" or lc[f"variability_flag_{band}_reject"] == False
        
        # check if there are valid points after the filter
        if mask.sum() == 0:
            # print(f"Warning: No valid points for band {band} in {folder_lc}")
            dict_per[band] = np.zeros_like(freq)
            without_points.append(folder_lc)
            continue

        # get the time, flux and flux_err of the light curve
        if band == "g":
            time_, flux_, flux_err_ = lc.loc[mask][["g_transit_time", "g_transit_flux", "g_transit_flux_error"]].values.T
        else:
            time_, flux_, flux_err_ = lc.loc[mask][[f"{band}_obs_time", f"{band}_flux", f"{band}_flux_error"]].values.T
        
        # verify that the time, flux and flux_err are not nan values
        time, flux, flux_err = filter_lists(time_, flux_, flux_err_)
        
        # calculate the periodogram
        periodogram = LombScargle(time, flux, flux_err).power(freq)
        # save the periodogram
        dict_per[band] = periodogram
        # multiband
        times += list(time)
        fluxes += list(flux)
        fluxes_err += list(flux_err)
        bands += [band]*len(time)
    # calculate the periodogram of the multiband
    periodogram = LombScargle(times, fluxes, bands, fluxes_err).power(freq)
    dict_per["multiband"] = periodogram
    # return the periodograms
    return d_folder_lc, dict_per
    
    
    
    

if __name__ == "__main__":
    
    # size of the batch
    batch_size = 32
    print(f"setting batch size to {batch_size}")
    without_points = []
    # read the valid light curves
    # valid_lightcurves = pd.read_csv(os.path.join("dataset", "valid_lightcurves.csv"))

    print("Initializing Ray")
    ray.init(num_cpus=4)
    print("Ray initialized")

    for folder in ["eclipsing_binary", "rrlyrae"]:
        # define name of folder specific of the type light curve
        d_folder_type = os.path.join("dataset", folder)
        print(f"Get values of the grid for {folder}")
        # get values of the grid
        grid = pd.read_csv(os.path.join("dataset", "grid.csv"))
        min_freq = grid[grid["type"] == folder]["low-frequency"].values[0]
        max_freq = grid[grid["type"] == folder]["high-frequency"].values[0]

        # define range of frequencies to calculate the periodogram
        print(f"calculating range of frequencies for {folder} from {min_freq} to {max_freq} with step 1e-4")
        freq = np.arange(min_freq, 2*max_freq, 1e-4)
        # save the frequencies
        np.savetxt(os.path.join("dataset", f"frequencies_{folder}.txt"), freq)
        print(f"Frequencies of {folder} saved in dataset/frequencies_{folder}.txt")

        print(f"calculating periodograms of {folder}")
        
        # batches for the directories
        directories = os.listdir(d_folder_type)
        dict_per = {}
        for i in tqdm(range(0, len(directories), batch_size), desc=f"Calculating periodograms of {folder}"):
            batch = directories[i:i+batch_size]
            # calculate periodograms
            results = ray.get([periodograms_band.remote(freq, d_folder_type, folder_lc, dict_per, without_points) for folder_lc in batch])
            profile = partial(timeit, globals=globals(), number=1)
            time_to_calculate = profile("ray.get([periodograms_band.remote(freq, d_folder_type, folder_lc, dict_per, without_points) for folder_lc in os.listdir(d_folder_type)])")
            
        print(f"Saving periodograms of {folder}")
        # save the periodograms with tqdm and message
        for result in tqdm(results, desc=f"Saving periodograms of {folder}"):
            d_folder_lc, dict_per = result
            # with open(os.path.join(d_folder_lc, f"periodograms_{folder_lc}.pkl"), "wb") as f:
            #     pickle.dump(dict_per, f, protocol=pickle.HIGHEST_PROTOCOL)
            
        # save the without points in a csv file
        pd.DataFrame(without_points, columns=["source_id"]).to_csv(os.path.join("dataset", f"without_points_{folder}.csv"), index=False)
        
        print(f"Time to calculate periodograms of {folder}: {time_to_calculate} seconds")
