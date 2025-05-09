from astroquery.gaia import Gaia 
import pandas as pd
import sys
import getpass
import pickle as pkl
import numpy as np
import matplotlib.pyplot as plt
import os

sys.path.append("..")

from matplotlib.gridspec import GridSpec

def plot_light_curve(time, mag, error, id_lc, type_lc, period=None):
    """
    Minimal light curve plot with error bars.
    
    Parameters:
    - time: Array of time values
    - mag: Array of magnitude values
    - error: Array of magnitude errors
    """
    plt.figure(figsize=(10, 5))
    plt.errorbar(time, mag, yerr=error, fmt='o', markersize=3, color='blue')
    # Add period line if provided
    if period is not None:
        plt.axvline(x=period, color='red', linestyle='--', 
                   linewidth=1, label=f'Period: {period:.2f}')
        # Add text annotation
        plt.text(period, np.min(mag), f'  {period:.2f}', 
                color='red', va='top')
    plt.gca().invert_yaxis()  # Proper magnitude scale (bright at bottom)
    plt.xlabel('Time')
    plt.ylabel('Magnitude')
    plt.title(f'Light Curve: {type_lc} (ID: {id_lc})')
    plt.grid(alpha=0.3)
    plt.savefig(f'figures/light_curve_{type_lc}_{id_lc}.png', dpi=300, bbox_inches='tight')
    print(f"Saved light curve to figures/light_curve_{type_lc}_{id_lc}.png")
    plt.close()


def plot_folded_light_curve(time, mag, error, period, id_lc, type_lc):
    """
    Plot a folded light curve and save it to a file.
    
    Parameters:
    - time: array-like, time values of observations
    - mag: array-like, magnitude values
    - error: array-like, error values for magnitudes
    - period: float, period to fold the light curve
    - id_lc: str, identifier for the light curve (used in filename)
    - type_lc: str, type of light curve (used in filename and title)
    """
    # Create the figure and axis
    plt.figure(figsize=(10, 6))
    
    # Fold the light curve
    folded_time = (time % period) / period
    
    # Sort by phase for better plotting
    sort_idx = np.argsort(folded_time)
    folded_time = folded_time[sort_idx]
    folded_mag = mag[sort_idx]
    folded_error = error[sort_idx]
    
    # Plot the folded light curve with error bars
    plt.errorbar(folded_time, folded_mag, yerr=folded_error, 
                fmt='o', markersize=3, capsize=2, 
                color='blue', alpha=0.7, label='Data')
    
    # Invert y-axis for magnitudes (higher values = fainter)
    plt.gca().invert_yaxis()
    
    # Set labels and title
    plt.xlabel('Phase')
    plt.ylabel('Magnitude')
    plt.title(f'Folded Light Curve: {type_lc} (ID: {id_lc}, Period: {period:.4f} days)')
    plt.grid(True, alpha=0.3)
    plt.legend()
    
    # Ensure the figures directory exists
    os.makedirs('../figures', exist_ok=True)
    
    # Save the figure
    filename = f'../figures/light_curve_folding_{type_lc}_{id_lc}.png'
    plt.savefig(filename, dpi=300, bbox_inches='tight')
    plt.close()
    
    print(f"Saved folded light curve to {filename}")


def plot_folded_light_curve_with_period(time, mag, error, period, id_lc, type_lc):
    """
    Plots a folded light curve with 1.5 phases and period marked
    
    Parameters:
    - time: Array of time values
    - mag: Array of magnitude values
    - error: Array of magnitude errors
    - period: Period to fold the light curve
    - lc_id: Light curve identifier (optional)
    - lc_type: Light curve type (optional)
    """
    plt.figure(figsize=(10, 6))
    
    # Fold the light curve and duplicate to 1.5 phases
    phase = (time % period) / period
    phase_extended = np.concatenate([phase, phase + 1])
    mag_extended = np.concatenate([mag, mag])
    error_extended = np.concatenate([error, error])
    
    # Plot with error bars
    plt.errorbar(phase_extended, mag_extended, yerr=error_extended,
                fmt='o', markersize=4, capsize=2,
                color='blue', alpha=0.7, label='Folded data')
    
    # Add vertical line at full period (phase=1.0)
    plt.axvline(x=1.0, color='red', linestyle='--', 
                linewidth=1.5, alpha=0.7, label=f'Period: {period:.4f}')
    
    # Add period text annotation
    y_range = np.max(mag) - np.min(mag)
    plt.text(1.02, np.min(mag) + 0.1*y_range, 
             f'Period = {period:.4f}',
             color='red', fontsize=10, ha='left')
    
    # Format plot
    plt.xlim(0, 1.5)
    plt.gca().invert_yaxis()
    plt.xlabel('Phase (Folded Period)')
    plt.ylabel('Magnitude')
    title = f'Folded Light Curve \n id: {id_lc} \n type: {type_lc} \n period: {period:.4f}'
    plt.title(title)
    plt.grid(alpha=0.3)
    plt.legend()
    
    plt.tight_layout()
    plt.savefig(f'figures/light_curve_folding_with_period_{type_lc}_{id_lc}.png', dpi=300, bbox_inches='tight')
    print(f"Saved folded light curve to figures/light_curve_folding_with_period_{type_lc}_{id_lc}.png")
    plt.close()
    


id_ecl = 999981777942644864

user = input("Username Gaia: ")
password = getpass.getpass("Password Gaia: ")

Gaia.login(user=user, password=password)


# query to get the periodo of the id 
for id, table in [(id_ecl, "vari_eclipsing_binary")]:
    if table == "vari_eclipsing_binary":
        query = f"""
        SELECT frequency
        FROM gaiadr3.{table}
        WHERE source_id = {id}
        """
    else:
        query = f"""
        SELECT pf
        FROM gaiadr3.{table} 
        WHERE source_id = {id}
        """
    result = Gaia.launch_job(query)
    results = result.get_results()
    print(f"results {table}: {results}")
    
# extract pf from dataset/valid_lightcurves.csv
df = pd.read_csv("dataset/valid_lightcurves.csv")
pf_ecl = df[df['source_id'] == id_ecl]['pf'].values[0]
# check if the period is the same CHECK
print(f"pf_ecl: {pf_ecl}")

# extract lc from dataset/{table}/{lc_id}/{lc_id}.pkl
lc_ecl = pd.read_pickle(f"dataset/eclipsing_binary/{id_ecl}/{id_ecl}.pkl")

# extract data from the light curve
time_ecl = lc_ecl["g_transit_time"]
mag_ecl = lc_ecl["g_transit_mag"]
flux_over_error_ecl = lc_ecl["g_transit_flux_over_error"]

err_ecl = 2.5/(np.log(10)*flux_over_error_ecl)

plot_light_curve(time_ecl, mag_ecl, err_ecl, id_ecl, "ECL") 

plot_folded_light_curve(time_ecl, mag_ecl, err_ecl, pf_ecl, id_ecl, "ECL")

plot_folded_light_curve_with_period(time_ecl, mag_ecl, err_ecl, pf_ecl, id_ecl, "ECL")








