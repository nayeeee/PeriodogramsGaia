import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import sys

sys.path.append("..")

def filter_flux_over_error(flux_over_error, time, mag):
    mask = (flux_over_error > 0) & (~np.isnan(time)) & (~np.isnan(mag))
    return flux_over_error[mask], time[mask], mag[mask]

def plot_folded_light_curve(time_dict, mag_dict, error_dict, period, id_lc, type_lc):
    """
    Plot a folded light curve (single phase 0-1) with multiple bands and save to file.
    
    Parameters:
    - time_dict: dict with bands ('g', 'bp', 'rp') as keys and time arrays as values
    - mag_dict: dict with bands ('g', 'bp', 'rp') as keys and magnitude arrays as values
    - error_dict: dict with bands ('g', 'bp', 'rp') as keys and error arrays as values
    - period: float, period to fold the light curve
    - id_lc: str, light curve identifier
    - type_lc: str, light curve type/classification
    """
    plt.figure(figsize=(10, 6))
    
    # Band styles configuration
    band_styles = {
        'g': {'color': 'green', 'marker': 'o', 'label': 'G band'},
        'bp': {'color': 'blue', 'marker': 's', 'label': 'BP band'},
        'rp': {'color': 'red', 'marker': '^', 'label': 'RP band'}
    }
    
    # Process and plot each band
    for band in time_dict.keys():
        if band not in mag_dict or band not in error_dict:
            print(f"Warning: Missing data for band {band}")
            continue
            
        time = np.array(time_dict[band])
        mag = np.array(mag_dict[band])
        error = np.array(error_dict[band])
        
        # Remove NaN values
        valid_mask = ~np.isnan(time) & ~np.isnan(mag) & ~np.isnan(error)
        time = time[valid_mask]
        mag = mag[valid_mask]
        error = error[valid_mask]
        
        if len(time) == 0:
            print(f"Warning: No valid data for band {band}")
            continue
            
        # Fold the light curve (phase 0-1)
        folded_phase = (time % period) / period
        
        # Sort by phase
        sort_idx = np.argsort(folded_phase)
        phase_sorted = folded_phase[sort_idx]
        mag_sorted = mag[sort_idx]
        error_sorted = error[sort_idx]
        
        # Plot with error bars
        plt.errorbar(phase_sorted, mag_sorted, yerr=error_sorted,
                    fmt=band_styles[band]['marker'], markersize=5,
                    capsize=2, color=band_styles[band]['color'],
                    alpha=0.7, label=band_styles[band]['label'])
    
    # Format plot
    plt.gca().invert_yaxis()
    plt.xlabel('Phase (0-1)', fontsize=12)
    plt.ylabel('Magnitude', fontsize=12)
    plt.title(f'Folded Light Curve: {type_lc} (ID: {id_lc})\nPeriod: {period:.4f} days', fontsize=12)
    plt.grid(True, alpha=0.3)
    plt.legend(loc='best', fontsize=10)
    
    # Set x-axis limits for single phase
    plt.xlim(0, 1)
    
    # Create output directory if needed
    os.makedirs(f'dataset10/{type_lc}/{id_lc}', exist_ok=True)
    
    # Save figure
    filename = f'dataset10/{type_lc}/{id_lc}/light_curve_folding_{id_lc}.png'
    plt.savefig(filename, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"Saved single-phase folded light curve to {filename}")

def plot_top_10_folded_light_curve(times, magnitudes, errors, top_per, band, id_lc, type_lc):
    """
    Plot top 10 folded light curves in a 5x2 grid for a specific band.
    
    Parameters:
    - times: dict with keys 'g', 'bp', 'rp', 'multiband' containing time arrays
    - magnitudes: dict with keys 'g', 'bp', 'rp', 'multiband' containing mag arrays
    - errors: dict with keys 'g', 'bp', 'rp', 'multiband' containing error arrays
    - top_per: array of top 10 periods to plot
    - band: reference band for these periods ('g', 'bp', 'rp', or 'multiband')
    - id_lc: str, light curve identifier
    - type_lc: str, light curve type/classification
    """
    # Create 5x2 figure
    fig, axes = plt.subplots(5, 2, figsize=(15, 20))
    fig.suptitle(f'Folded Light Curve: {type_lc} (ID: {id_lc})\nTop 10 periods from {band} band', 
                 y=1.02, fontsize=14)
    
    # Band styles configuration
    band_styles = {
        'g': {'color': 'green', 'marker': 'o', 'label': 'G band'},
        'bp': {'color': 'blue', 'marker': 's', 'label': 'BP band'},
        'rp': {'color': 'red', 'marker': '^', 'label': 'RP band'},
        'multiband': {'color': 'purple', 'marker': '*', 'label': 'Multiband'}
    }
    
    # Plot each period in a subplot
    for i, period in enumerate(top_per):
        ax = axes[i//2, i%2]  # Get current axis (5 rows, 2 columns)
        
        # Plot each band
        for b in ['g', 'bp', 'rp']:
            if b not in times or b not in magnitudes or b not in errors:
                continue
                
            time = np.array(times[b])
            mag = np.array(magnitudes[b])
            err = np.array(errors[b])
            
            # Remove NaN values
            valid_mask = ~np.isnan(time) & ~np.isnan(mag) & ~np.isnan(err)
            time = time[valid_mask]
            mag = mag[valid_mask]
            err = err[valid_mask]
            
            if len(time) == 0:
                continue
                
            # Fold the light curve
            folded_phase = (time % period) / period
            sort_idx = np.argsort(folded_phase)
            
            ax.errorbar(folded_phase[sort_idx], mag[sort_idx], yerr=err[sort_idx],
                       fmt=band_styles[b]['marker'], markersize=3,
                       capsize=1.5, color=band_styles[b]['color'],
                       alpha=0.7, label=band_styles[b]['label'])
        
        ax.invert_yaxis()
        ax.set_xlabel('Phase')
        ax.set_ylabel('Magnitude')
        ax.set_title(f'Period top {i+1}: {period:.6f} days', fontsize=10)
        ax.grid(True, alpha=0.3)
        
        # Add legend only to first subplot
        if i == 0:
            ax.legend(loc='upper right', fontsize=8)
    
    plt.tight_layout()
    
    # Save figure
    filename = f'dataset10/{type_lc}/{id_lc}/top_{band}_light_curve_folding_{id_lc}.png'
    plt.savefig(filename, dpi=150, bbox_inches='tight')
    plt.close()
    print(f"Saved top 10 folded light curves to {filename}")
 
def main():
    # set directory
    directory = "dataset10"
    # extract pf from dataset/valid_lightcurves.csv
    periods_lightcurves = pd.read_csv(f"{directory}/valid_lightcurves.csv")
    print(f"periods_lightcurves: {periods_lightcurves}")
    # set folder type
    for folder_type in ["eclipsing_binary", "rrlyrae"]:
        # set folder type directory
        d_folder_type = os.path.join(directory, folder_type)
        # list of light curves
        list_lc = os.listdir(d_folder_type)

        for name_lc in list_lc:
            # read matrix from {d_folder_type}/{lc_id}/error_matrixes_{lc_id}.pkl
            error_matrixes = pd.read_pickle(f"{d_folder_type}/{name_lc}/error_matrixes_{name_lc}.pkl")
            top_periods = {}
            for band in ['g', 'bp', 'rp', 'multiband']:
                # transform frequency to period
                top_periods[band] = 1/np.array(error_matrixes[band][0])
                # print the error matrixes
                print(f"top_period {band}: {top_periods[band][0]}")
            
            # pf of the light curves
            print(f"pf of {name_lc}: {periods_lightcurves[periods_lightcurves['source_id'] == int(name_lc)]['pf'].values[0]}")
            pf = periods_lightcurves[periods_lightcurves['source_id'] == int(name_lc)]['pf'].values[0]
            print(f"pf: {pf}")
            # extract lc from dataset/{table}/{lc_id}/{lc_id}.pkl
            lc = pd.read_pickle(f"{d_folder_type}/{name_lc}/{name_lc}.pkl")
            times = {}
            magnitudes = {}
            errors = {}
            for band in ['g', 'bp', 'rp']:
                if band == 'g':
                    times[band], magnitudes[band], flux_over_error = lc["g_transit_time"], lc["g_transit_mag"], lc["g_transit_flux_over_error"]
                else:
                    times[band], magnitudes[band], flux_over_error = lc[f"{band}_obs_time"], lc[f"{band}_mag"], lc[f"{band}_flux_over_error"]
                # filter the data
                flux_over_error, times[band], magnitudes[band] = filter_flux_over_error(flux_over_error, times[band], magnitudes[band])
                errors[band] = 2.5/(np.log(10)*flux_over_error)
            # plot the light curve
            plot_folded_light_curve(times, magnitudes, errors, pf, name_lc, folder_type)
            
            for band in ['g', 'bp', 'rp']:
                # plot with top 10 periods
                plot_top_10_folded_light_curve(times, magnitudes, errors, top_periods[band], band, name_lc, folder_type)

if __name__ == "__main__":
    main()