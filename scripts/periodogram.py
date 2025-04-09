import pandas as pd
import numpy as np
from astropy.timeseries import LombScargle
import os
import pickle

def filter_flux_over_error(flux_over_error, time, mag):
    """Filter out negative flux_over_error values"""
    mask = flux_over_error > 0
    return flux_over_error[mask], time[mask], mag[mask]

def calculate_single_periodogram(lc_path, freq_path=None):
    """
    Calculate periodograms for a single light curve
    
    Parameters:
    -----------
    lc_path : str
        Path to the light curve pickle file
    freq_path : str, optional
        Path to the frequencies file. If None, will generate default frequencies
    
    Returns:
    --------
    dict
        Dictionary containing periodograms for each band and multiband
    """
    # Read the light curve
    lc = pd.read_pickle(lc_path)
    
    # Read or generate frequencies
    if freq_path and os.path.exists(freq_path):
        freq = np.loadtxt(freq_path)
    else:
        freq = np.arange(1e-3, 25, 1e-4)  # Default frequency range
    
    # Initialize lists for multiband analysis
    times, magnitudes, errors, bands = [], [], [], []
    dict_per = {}
    
    # Calculate periodogram for each band
    for band in ["g", "bp", "rp"]:
        # Get the mask for valid points
        mask = lc[f"variability_flag_{band}_reject"] == "false"
        
        if sum(mask) == 0:
            print(f"No valid points for band {band}")
            continue
        
        # Get time, magnitude and flux_over_error
        if band == "g":
            time_, mag_, flux_over_error_ = lc.loc[mask][["g_transit_time", "g_transit_mag", "g_transit_flux_over_error"]].values.T
        else:
            time_, mag_, flux_over_error_ = lc.loc[mask][[f"{band}_obs_time", f"{band}_mag", f"{band}_flux_over_error"]].values.T
        
        # Filter and calculate errors
        flux_over_error, time, mag = filter_flux_over_error(flux_over_error_, time_, mag_)
        err = 2.5/(np.log(10)*flux_over_error)
        
        try:
            # Calculate periodogram for this band
            periodogram = LombScargle(time, mag, err).power(freq)
            dict_per[band] = periodogram
            
            # Store data for multiband analysis
            times.extend(time)
            magnitudes.extend(mag)
            errors.extend(err)
            bands.extend([band]*len(time))
            
        except Exception as e:
            print(f"Error calculating periodogram for band {band}: {e}")
            continue
    
    # Calculate multiband periodogram
    if times:  # Only if we have data
        periodogram = LombScargle(times, magnitudes, errors, bands).power(freq)
        dict_per["multiband"] = periodogram
    
    return dict_per

if __name__ == "__main__":
    # Example usage
    lc_folder = "dataset"
    for name_lc in ["4050275694921784704", "4103678042580890752", "6027794498969446400"]:
        lc_path = os.path.join(lc_folder, f"rrlyrae/{name_lc}/{name_lc}.pkl")
        # Calculate periodograms
        periodograms = calculate_single_periodogram(lc_path)
        
        # Save results
        output_path = os.path.join(lc_folder, f"periodograms_{name_lc}.pkl")
        with open(output_path, "wb") as f:
            pickle.dump(periodograms, f, protocol=pickle.HIGHEST_PROTOCOL)
    
    print(f"Periodograms saved to {output_path}")