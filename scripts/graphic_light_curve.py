import matplotlib.pyplot as plt
import pickle as pkl
import os
import numpy as np

def graphic_lc(lc, type_lc):
    fig, ax = plt.subplots(figsize=(6, 4), tight_layout=True)
    # define new form depend of band
    for band, form in [("g", 'o'), ("bp", 's'), ("rp", 'x')]: #[("g", 'o'), ("bp", 's'), ("rp", 'x')]
        mask = lc[f"variability_flag_{band}_reject"] == "false"
        if band == "g":
            time, mag, flux_over_error = lc.loc[mask][["g_transit_time", "g_transit_mag", "g_transit_flux_over_error"]].values.T
        else:
            time, mag, flux_over_error = lc.loc[mask][[f"{band}_obs_time", f"{band}_mag", f"{band}_flux_over_error"]].values.T
        err = 2.5/(np.log(10)*flux_over_error)
        print(f"point {band} time: {len(time)}, mag: {len(mag)}, flux_over_error: {len(flux_over_error)}")
        print(f"time: {time}\n mag: {mag}\n flux_over_error: {flux_over_error}")
        # size of the point
        size = 3
        ax.errorbar(time, mag, err, fmt=form, label=band, markersize=size)
        
    ax.set_xlabel('Time')
    ax.set_ylabel('Magnitude')
    ax.set_title(f'{type_lc} source_id: {lc["source_id"].loc[0]}')
    ax.legend();
    
    # save figure
    plt.savefig(f"figures/graphic_lc_{type_lc}_{lc['source_id'].loc[0]}.png")
    print(f"Graphic saved in figures/graphic_lc_{type_lc}_{lc['source_id'].loc[0]}.png")
    plt.close()

def main():
    
    # create the directory if not exists
    if not os.path.exists("figures"):
        os.makedirs("figures")

    for name_lc in ["2252805218287938560"]:
        print(f"Processing {name_lc}")
        # define the directory of the light curve
        directory_lc = f"dataset/eclipsing_binary/{name_lc}/{name_lc}.pkl"
        type_lc = "eclipsing_binary"
        # read file .pkl
        with open(directory_lc, "rb") as f:
            lc = pkl.load(f)
        # graphic light curve
        graphic_lc(lc, type_lc)

if __name__ == "__main__":
    main()

