# calculate the periodograms of the light curves
import sys 
import os
import pandas as pd
import numpy as np
import pickle
import ray
from functools import partial

sys.path.append("..")

@ray.remote(num_cpus=4)
def periodograms_band(freq, d_folder_type, folder_lc, valid_lightcurves):
    # path of the light curve
    d_folder_lc = os.path.join(d_folder_type, folder_lc)
    lc = pd.read_pickle(os.path.join(d_folder_lc, folder_lc+'.pkl'))
    # name of the light curve
    name_lc = lc.source_id.iloc[0]
    # period of the light curve
    period = valid_lightcurves[valid_lightcurves["source_id"] == name_lc]['pf'].values[0]

    # initialize list of time, flux and flux_err to multiband
    times, fluxes, fluxes_err, bands = [], [], [], []
    # calculate the periodogram for each band and multiband
    for band in ["g", "bp", "rp"]:
        # get the mask of the light curve
        mask = lc[f"variability_flag_{band}_reject"] == "True"
        # get the time, flux and flux_err of the light curve
        if band == "g":
            time, flux, flux_err = lc.loc[mask][["g_transit_time", "g_transit_flux", "g_transit_flux_error"]].values.T
        else:
            time, flux, flux_err = lc.loc[mask][[f"{band}_obs_time", f"{band}_flux", f"{band}_flux_error"]].values.T
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
    print("Loading valid light curves")
    # read the valid light curves
    valid_lightcurves = pd.read_csv(os.path.join("dataset", "valid_lightcurves.csv"))
    print("Valid light curves loaded")

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
        # calculate periodograms
        results = ray.get([periodograms_band.remote(freq, d_folder_type, folder_lc, valid_lightcurves) for folder_lc in os.listdir(d_folder_type)])
        print(f"profile of the calculation of periodograms of {folder}")
        profile = partial(timeit, globals=globals(), number=1)
        time_to_calculate = profile("ray.get([periodograms_band.remote(freq, d_folder_type, folder_lc, valid_lightcurves) for folder_lc in os.listdir(d_folder_type)])")
        
        print(f"Saving periodograms of {folder}")
        # save the periodograms with tqdm and message
        for result in tqdm(results, desc=f"Saving periodograms of {folder}"):
            d_folder_lc, dict_per = result
            # with open(os.path.join(d_folder_lc, f"periodograms_{folder_lc}.pkl"), "wb") as f:
            #     pickle.dump(dict_per, f, protocol=pickle.HIGHEST_PROTOCOL)
        
        print(f"Time to calculate periodograms of {folder}: {time_to_calculate} seconds")
