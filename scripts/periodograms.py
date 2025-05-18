# calculate the periodograms of the light curves
import sys 
import os
import pandas as pd
import numpy as np
import pickle
import ray
import warnings

from tqdm import tqdm
from functools import partial
from astropy.timeseries import LombScargle
from astropy.timeseries import LombScargleMultiband
from timeit import timeit
from functools import partial

sys.path.append("..")
 
cpus_per_task = 1  # CPUs per task
total_cpus = 62    # Total CPUs available

# function for discard the values of the flux_over_error that are not positive
def filter_flux_over_error_and_nan(flux_over_error, time, mag):
    # mask with the values of the flux_over_error that are positive and not nan
    mask = (flux_over_error > 0) & (~np.isnan(time)) & (~np.isnan(mag))
    # filter the values of the flux_over_error, time and mag
    err = flux_over_error[mask]
    time_filtered = time[mask]
    mag_filtered = mag[mask]
    return np.array(err), np.array(time_filtered), np.array(mag_filtered)

@ray.remote(num_cpus=cpus_per_task)
def periodograms_band(freq, d_folder_type, folder_lc, L, M):
    # path of the light curve
    d_folder_lc = os.path.join(d_folder_type, folder_lc)
    lc = pd.read_pickle(os.path.join(d_folder_lc, folder_lc+'.pkl'))
    # name of the light curve
    name_lc = lc.source_id.iloc[0]
    dict_per = {}

    # initialize list of time, mag and mag_err to multiband
    times, magnitudes, errors, bands = [], [], [], []

    with_problems = []
    with_warnings = []
    # calculate the periodogram for each band and multiband
    for band in ["g", "bp", "rp"]:
        # get the mask of the light curve
        mask = lc[f"variability_flag_{band}_reject"] == "false"
        
        # VERIFY THAT THE MASK CONTENT VALUES TRUE  
        # get the time, mag and mag_err of the light curve
        if band == "g":
            time_, mag_, flux_over_error_ = lc.loc[mask][["g_transit_time", "g_transit_mag", "g_transit_flux_over_error"]].values.T
        else:
            time_, mag_, flux_over_error_ = lc.loc[mask][[f"{band}_obs_time", f"{band}_mag", f"{band}_flux_over_error"]].values.T

        flux_over_error, time, mag = filter_flux_over_error_and_nan(flux_over_error_, time_, mag_)
        
        
        # extract the error of the mag from this formula: 2.5/(np.log(10)*flux_over_error)
        err = 2.5/(np.log(10)*flux_over_error)
        # print(f"band: {band} lombscargle\n len time: {len(time)}, len mag: {len(mag)}, len err: {len(err)}")
        try:    
            with warnings.catch_warnings(record=True) as w:
                # capture all warnings
                warnings.simplefilter("always")
                
                # calculate the periodogram
                periodogram = LombScargle(time, mag, err).power(freq)
                # save the periodogram
                dict_per[band] = periodogram
                
                if any(issubclass(warning.category, RuntimeWarning) for warning in w):
                    # messages of the warnings
                    messages = [warning.message for warning in w]
                    with_warnings.append((name_lc, band, messages))
                    # print(f"Warning in {name_lc} in {band}: {messages}")
                    
        except Exception as e:
            # print(f"Error in {name_lc} in {band}: {e}")
            with_problems.append((name_lc, band))
            continue
        # multiband
        times += list(time)
        magnitudes += list(mag)
        errors += list(err)
        bands += [band]*len(time)
    # print(f"multiband lombscargle\n len times: {len(times)}, len magnitudes: {len(magnitudes)}, len errors: {len(errors)}, len bands: {len(bands)}")
    # calculate the periodogram of the multiband
    # corregir método de LombScargleMultiband # CORREGIR
    periodogram_multiband = LombScargleMultiband(t=times, y=magnitudes, bands=bands, dy=errors).power(freq)
    dict_per["multiband"] = periodogram_multiband 
    
    # return the periodograms
    return {'d_folder_lc': d_folder_lc, 'dict_per': dict_per, 'with_problems': with_problems, 'with_warnings': with_warnings}
    
    
    
    

if __name__ == "__main__":
    # parameters
    L = 10
    M = 18
    concurrent_tasks = total_cpus // cpus_per_task  # = 16 tasks simultaneously
    batch_size = concurrent_tasks * 2  # = 32 to have two rounds of tasks
    print(f"setting batch size to {batch_size}")
    # read the valid light curves
    # valid_lightcurves = pd.read_csv(os.path.join("dataset", "valid_lightcurves.csv"))

    print("Initializing Ray")
    ray.init(num_cpus=total_cpus)
    print("Ray initialized")
    
    # define range of frequencies to calculate the periodogram
    print(f"calculating range of frequencies from 1e-3 to 25 with step 1e-4")
    freq = np.arange(1e-3, 25, 1e-4)
    # save the frequencies
    np.savetxt(os.path.join("dataset", f"frequencies.txt"), freq)
    print(f"Frequencies saved in dataset/frequencies.txt")

    # "eclipsing_binary", "rrlyrae"
    for folder in ["eclipsing_binary"]: 
        # define name of folder specific of the type light curve
        d_folder_type = os.path.join("dataset", folder)

        print(f"calculating periodograms of {folder}")
        
        # directories in the folder
        directories = [line for line in os.listdir(d_folder_type)]
        for i in tqdm(range(0, len(directories), batch_size), desc=f"Calculating periodograms of {folder}"):
            batch = directories[i:i+batch_size]
            # calculate periodograms
            results = ray.get([periodograms_band.remote(freq, d_folder_type, folder_lc, L, M) for folder_lc in batch])
            
            print(f"Saving periodograms of {folder}")
            lc_with_problems = [] 
            lc_with_warnings = []
            # save the periodograms with tqdm and message
            for result in results:
                # save the results
                lc_with_problems.extend(result['with_problems'])
                lc_with_warnings.extend(result['with_warnings'])
                # save the periodograms
                # overwrite the file if it exists
                if os.path.exists(os.path.join(result['d_folder_lc'], f"periodograms.pkl")):
                    os.remove(os.path.join(result['d_folder_lc'], f"periodograms.pkl"))
                with open(os.path.join(result['d_folder_lc'], f"periodograms.pkl"), "wb") as f:
                    pickle.dump(result['dict_per'], f, protocol=pickle.HIGHEST_PROTOCOL) 
            # Append the new results to the CSV files
            for logs in [(lc_with_problems, "with_problems"), (lc_with_warnings, "with_warnings")]:
                if logs[0]:
                    if logs[1] != "with_warnings":
                        df = pd.DataFrame(logs[0], columns=["source_id", "band"])
                    else:
                        df = pd.DataFrame(logs[0], columns=["source_id", "band", "warning"])
                    
                    if not os.path.exists(os.path.join("dataset", f"{logs[1]}_{folder}.csv")):
                        df.to_csv(os.path.join("dataset", f"{logs[1]}_{folder}.csv"), index=False)
                    else:
                        df.to_csv(os.path.join("dataset", f"{logs[1]}_{folder}.csv"), 
                                 mode='a', header=False, index=False)
                        
# OUTPUT:
# 
# Calculating periodograms of rrlyrae: 100%|████████████████████████████████████████████████████████████████████████████████| 1913/1913 [20:42:35<00:00, 38.97s/it]
# 
# Calculating periodograms of eclipsing_binary: 100%|██████████████████████████████████████████████████████████████████████| 7415/7415 [100:50:38<00:00, 48.96s/it]
# 
# 