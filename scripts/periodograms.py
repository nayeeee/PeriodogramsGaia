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

# function for discard the values of the flux_over_error that are not positive
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

@ray.remote(num_cpus=64)
def periodograms_band(freq, d_folder_type, folder_lc, without_points, lc_with_problems):
    # path of the light curve
    d_folder_lc = os.path.join(d_folder_type, folder_lc)
    lc = pd.read_pickle(os.path.join(d_folder_lc, folder_lc+'.pkl'))
    # name of the light curve
    name_lc = lc.source_id.iloc[0]
    # print(f"Calculating periodograms of {name_lc}")
    # period of the light curve
    # period = valid_lightcurves[valid_lightcurves["source_id"] == name_lc]['pf'].values[0]
    dict_per = {}

    # initialize list of time, mag and mag_err to multiband
    times, magnitudes, errors, bands = [], [], [], []
    # calculate the periodogram for each band and multiband
    for band in ["g", "bp", "rp"]:
        # get the mask of the light curve
        mask = lc[f"variability_flag_{band}_reject"] == "false" # VERIFY THAT THIS FILTER IS CORRECT
        
        if sum(mask) == 0:
            print(f"No points for {name_lc} in {band}")
            without_points.append(name_lc)
            continue
        
        # VERIFY THAT THE MASK CONTENT VALUES TRUE  
        # get the time, mag and mag_err of the light curve
        if band == "g":
            time_, mag_, flux_over_error_ = lc.loc[mask][["g_transit_time", "g_transit_mag", "g_transit_flux_over_error"]].values.T
        else:
            time_, mag_, flux_over_error_ = lc.loc[mask][[f"{band}_obs_time", f"{band}_mag", f"{band}_flux_over_error"]].values.T

        time, mag, flux_over_error = filter_flux_over_error(flux_over_error_, time_, mag_)
        # extract the error of the mag from this formula: 2.5/(np.log(10)*flux_over_error)
        err = 2.5/(np.log(10)*flux_over_error)
        # print(f"band: {band} lombscargle\n len time: {len(time)}, len mag: {len(mag)}, len err: {len(err)}")
        try:    
            # calculate the periodogram
            periodogram = LombScargle(time, mag, err).power(freq)
            # save the periodogram
            dict_per[band] = periodogram
        except Exception as e:
            print(f"Error in {name_lc} in {band}: {e}")
            lc_with_problems.append(name_lc)
            continue
        # multiband
        times += list(time)
        magnitudes += list(mag)
        errors += list(err)
        bands += [band]*len(time)
    # print(f"multiband lombscargle\n len times: {len(times)}, len magnitudes: {len(magnitudes)}, len errors: {len(errors)}, len bands: {len(bands)}")
    # calculate the periodogram of the multiband
    periodogram = LombScargle(times, magnitudes, errors, bands).power(freq)
    dict_per["multiband"] = periodogram
    # return the periodograms
    return d_folder_lc, dict_per, without_points, lc_with_problems
    
    
    
    

if __name__ == "__main__":
    
    # size of the batch
    batch_size = 3200
    print(f"setting batch size to {batch_size}")
    without_points = []
    lc_with_problems = []
    # read the valid light curves
    # valid_lightcurves = pd.read_csv(os.path.join("dataset", "valid_lightcurves.csv"))

    print("Initializing Ray")
    ray.init(num_cpus=64)
    print("Ray initialized")
    
    # define range of frequencies to calculate the periodogram
    print(f"calculating range of frequencies from 1e-3 to 25 with step 1e-4")
    freq = np.arange(1e-3, 25, 1e-4)
    # save the frequencies
    np.savetxt(os.path.join("dataset", f"frequencies.txt"), freq)
    print(f"Frequencies saved in dataset/frequencies.txt")

    # "eclipsing_binary", "rrlyrae"
    for folder in ["rrlyrae"]: 
        # define name of folder specific of the type light curve
        d_folder_type = os.path.join("dataset", folder)

        print(f"calculating periodograms of {folder}")
        
        # batches for the directories
        directories = os.listdir(d_folder_type)
        for i in tqdm(range(0, len(directories), batch_size), desc=f"Calculating periodograms of {folder}"):
            batch = directories[i:i+batch_size]
            # calculate periodograms
            results = ray.get([periodograms_band.remote(freq, d_folder_type, folder_lc, without_points, lc_with_problems) for folder_lc in batch])
            profile = partial(timeit, globals=globals(), number=1)
            time_to_calculate = profile("ray.get([periodograms_band.remote(freq, d_folder_type, folder_lc, dict_per, without_points, lc_with_problems) for folder_lc in os.listdir(d_folder_type)])")
            
            print(f"Saving periodograms of {folder} from the batch {batch}")
            # save the periodograms with tqdm and message
            for result in tqdm(results, desc=f"Saving periodograms of {folder}"):
                d_folder_lc, dict_per, without_points, lc_with_problems = result
                with open(os.path.join(d_folder_lc, f"periodograms.pkl"), "wb") as f:
                    pickle.dump(dict_per, f, protocol=pickle.HIGHEST_PROTOCOL)
                
            # Append the new results to the CSV files
            if without_points:
                df_without = pd.DataFrame(without_points, columns=["source_id"])
                if not os.path.exists(os.path.join("dataset", f"without_points_{folder}.csv")):
                    df_without.to_csv(os.path.join("dataset", f"without_points_{folder}.csv"), index=False)
                else:
                    df_without.to_csv(os.path.join("dataset", f"without_points_{folder}.csv"), 
                                    mode='a', header=False, index=False)

            if lc_with_problems:
                df_problems = pd.DataFrame(lc_with_problems, columns=["source_id"])
                if not os.path.exists(os.path.join("dataset", f"lc_with_problems_{folder}.csv")):
                    df_problems.to_csv(os.path.join("dataset", f"lc_with_problems_{folder}.csv"), index=False)
                else:
                    df_problems.to_csv(os.path.join("dataset", f"lc_with_problems_{folder}.csv"), 
                                     mode='a', header=False, index=False)

            print(f"Time to calculate periodograms of {folder}: {time_to_calculate} seconds")
