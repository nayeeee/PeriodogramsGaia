# filter dataset

# 1.- Extract N examples or all:
# * where pf or frequency is not null 
# * L points in each band 
# * average magnitude in band G < M
# * flux_over_error > 0

import pandas as pd
import os
from tqdm import tqdm
import numpy as np
import math
import sys
sys.path.append("..")
from astroquery.gaia import Gaia
import getpass

# STEP 2: Filter the dataset

# function for discard the values of the flux_over_error that are not positive
def filter_flux_over_error_and_nan(flux_over_error, time, mag):
    # mask with the values of the flux_over_error that are positive and not nan
    mask = (flux_over_error > 0) & (~np.isnan(time)) & (~np.isnan(mag))
    return mask

def chunks(lst, n):
    """
    Split an input list into multiple chunks of size =< n
    """
    for i in range(0, len(lst), n):
        yield lst[i:i + n]
        
def verification_lc(lc, path, type_star, L, M):
    # see if the mask is not empty for time, flux and flux_err for any band
    mask_g = lc["variability_flag_g_reject"]=="false"
    mask_bp = lc["variability_flag_bp_reject"]=="false"
    mask_rp = lc["variability_flag_rp_reject"]=="false"

    name = lc.source_id[0]
    
    lc_g = lc.loc[mask_g]
    lc_bp = lc.loc[mask_bp]
    lc_rp = lc.loc[mask_rp]

    common_columns = ['solution_id', 'source_id', 'transit_id', 'g_transit_time']
    columns_g  = ['g_transit_flux', 'g_transit_flux_error', 'g_transit_flux_over_error', 'g_transit_mag', 'variability_flag_g_reject', 'g_other_flags']
    columns_bp = ['bp_obs_time', 'bp_flux', 'bp_flux_error', 'bp_flux_over_error', 'bp_mag', 'variability_flag_bp_reject', 'bp_other_flags']
    columns_rp = ['rp_obs_time', 'rp_flux', 'rp_flux_error', 'rp_flux_over_error', 'rp_mag', 'variability_flag_rp_reject', 'rp_other_flags']

    lc_g = lc_g[common_columns + columns_g]
    lc_bp = lc_bp[common_columns + columns_bp]
    lc_rp = lc_rp[common_columns + columns_rp]
    
    # filter the flux_over_error that are not positive
    mask_g = filter_flux_over_error_and_nan(lc_g["g_transit_flux_over_error"], lc_g["g_transit_time"], lc_g["g_transit_mag"])
    mask_bp = filter_flux_over_error_and_nan(lc_bp["bp_flux_over_error"], lc_bp["bp_obs_time"], lc_bp["bp_mag"])
    mask_rp = filter_flux_over_error_and_nan(lc_rp["rp_flux_over_error"], lc_rp["rp_obs_time"], lc_rp["rp_mag"])
    
    lc_g = lc_g.loc[mask_g]
    lc_bp = lc_bp.loc[mask_bp]
    lc_rp = lc_rp.loc[mask_rp]
    
    points_G = lc_g.shape[0]
    points_BP = lc_bp.shape[0]
    points_RP = lc_rp.shape[0]
    mag_mean_G = np.mean(lc_g["g_transit_mag"])

    # see if the light curve fulfills the conditions of points in each band, average magnitude in the G band and that it is not repeated. Also that the mask is not empty for any band
    if ((points_BP >= L) & (points_G >= L) & (points_RP >= L) & (mag_mean_G < M)):
        # create folder for each lc
        parent_dir = os.path.join(path, type_star)
        path_lc = os.path.join(parent_dir, str(name))
        if not os.path.exists(path_lc):
            os.mkdir(path_lc) 
        path_lc = os.path.join(path_lc, str(name)+'.pkl') 
        if type_star == "eclipsing_binary":
            # remove the file if it exists
            if os.path.exists(path_lc):
                os.remove(path_lc)
            lc.to_pickle(path_lc)
        
        return True, name   
    
    return False, name

def create_folder_dataset():
    parent_dir = "dataset"
    if not os.path.exists(parent_dir):
        os.mkdir(parent_dir)
    directories = ["eclipsing_binary", "rrlyrae"]
    for directory in directories:
        path = os.path.join(parent_dir, directory)
        if not os.path.exists(path):
            os.mkdir(path)
            print(f"folder {path} created")
    return 

def initialize_csv_files():
    # Create CSV for valid light curves
    parent_dir = "dataset"
    valid_csv = os.path.join(parent_dir, "new_valid_lightcurves.csv")
    if not os.path.exists(valid_csv):
        with open(valid_csv, 'w') as f:
            f.write("source_id,pf,type\n")
    
    # Create CSV for invalid light curves
    invalid_csv = os.path.join(parent_dir, "new_invalid_lightcurves.csv")
    if not os.path.exists(invalid_csv):
        with open(invalid_csv, 'w') as f:
            f.write("source_id,type\n")
    
    return valid_csv, invalid_csv

if __name__ == "__main__":
    
    CHUNK_SIZE = 4900
    L = 10
    M = 18
    data_global = pd.DataFrame()
    
    print(f"Creating dataset folder...")
    create_folder_dataset()
    
    # Initialize CSV files
    valid_csv, invalid_csv = initialize_csv_files()
    
    # login to Gaia
    user = input("Username Gaia: ")
    password = getpass.getpass("Password Gaia: ")
    Gaia.login(user=user, password=password)
    
    # reads csv files with the results of the query
    # ["vari_eclipsing_binary", "vari_rrlyrae"]
    for table in ["vari_rrlyrae", "vari_eclipsing_binary"]: 
        valid_lc = 0
        not_valid_lc = 0
        # load results
        print(f"Loading results in {table}.csv...")
        path_results = os.path.join(f"dataset/{table}.csv")
        results = pd.read_csv(path_results)
        print(f"Results loaded in {table}.csv")

        # extract source_id
        ids = results["source_id"].tolist()  
        
        # extract per chunk of 4900 (https://www-cosmos-esa-int.translate.goog/web/gaia-users/archive/datalink-products?_x_tr_sl=en&_x_tr_tl=es&_x_tr_hl=es&_x_tr_pto=tc#datalink_jntb_get_above_lim)
        print(f"Chunks: {math.ceil(len(ids) / CHUNK_SIZE)} with CHUNK_SIZE = {CHUNK_SIZE}")
        ids_chunks = list(chunks(ids, CHUNK_SIZE)) ##  cut the list in the chunk end (list of lists with ids per chunk)
        
        print(f"Extracting light curves from Gaia DR3...")
        # extract light curves from Gaia DR3
        for i, chunk in tqdm(enumerate(ids_chunks), total=len(ids_chunks), desc=f"Processing {table} chunks"):
            # list to accumulate results of the chunk
            valid_results = []
            invalid_results = []
            
            # extract light curves from Gaia DR3
            datalink = Gaia.load_data(ids=chunk, 
                            data_release='Gaia DR3', 
                            retrieval_type='EPOCH_PHOTOMETRY', 
                            format='csv')
            
            print(f"Light curves extracted from Gaia DR3 from the chunk {i}")
            print(f"Filtering light curves from the chunk {i}...")
            # filter light curves
            for _, (key, value) in enumerate(datalink.items()):
                lc = value[0].to_pandas()
                is_valid, name = verification_lc(lc, "dataset", table[5:], L, M)
                
                # Get original light curve information
                source_info = results[results['source_id'] == name].iloc[0]
                
                if is_valid:
                    # Calculate pf according to the type of star
                    if table == "vari_eclipsing_binary":
                        pf = 1/source_info['frequency']
                    else:
                        if pd.notnull(source_info['pf']):
                            pf = source_info['pf']
                        else:
                            pf = source_info['p1_o']
                        
                    valid_results.append(f"{name},{pf},{table[5:]}\n")
                    print(f"Light curve {name} from chunk {i} is VALID")
                    valid_lc += 1
                else:
                    # Write in the invalid CSV
                    invalid_results.append(f"{name},{table[5:]}\n")
                    print(f"Light curve {name} from chunk {i} is NOT valid")
                    not_valid_lc += 1
                    
            # Write all results of the chunk at once
            if valid_results:
                with open(valid_csv, 'a') as f:
                    f.writelines(valid_results)
            
            if invalid_results:
                with open(invalid_csv, 'a') as f:
                    f.writelines(invalid_results)
            print(f"All light curves filtered from the chunk {i}")
            
        print(f"total light curves filtered in {table}: {valid_lc} / {len(ids)}")
        print(f"{(len(ids)-valid_lc)*100/len(ids)}% of the light curves were deleted with filters:\n - L points in each band \n - average magnitude in band G < M \n - flux_over_error > 0")

# OUTPUT:
# Processing vari_rrlyrae chunks: 100%|████████████████████████████████████████████████████████████████████████████Processing vari_rrlyrae chunks: 100%|███████████████████████████████████████████████████████████████████████████████████████████| 37/37 [2:35:00<00:00, 251.37s/it]
# total light curves filtered in vari_rrlyrae: 81515 / 177357
# 54.03902862587888% of the light curves were deleted with filters:
#  - L points in each band
#  - average magnitude in band G < M
# -------------------------------------------
# All light curves filtered from the chunk 445
# total light curves filtered in vari_eclipsing_binary: 945705 / 2184477
# 56.70794428140008% of the light curves were deleted with filters:
#  - L points in each band
#  - average magnitude in band G < M
# Processing vari_eclipsing_binary chunks: 100%|██████████| 446/446 [11:48:19<00:00, 95.29s/it]

# OFICIAL OUTPUT:
# Processing vari_rrlyrae chunks: 100%|██████████| 56/56 [1:27:33<00:00, 93.82s/it]
# All light curves filtered from the chunk 55
# total light curves filtered in vari_rrlyrae: 117292 / 271779
# 56.84287601323134% of the light curves were deleted with filters:
#  - L points in each band
#  - average magnitude in band G < M
# -------------------------------------------
# All light curves filtered from the chunk 445
# total light curves filtered in vari_eclipsing_binary: 945705 / 2184477
# 56.70794428140008% of the light curves were deleted with filters:
#  - L points in each band
#  - average magnitude in band G < M
# Processing vari_eclipsing_binary chunks: 100%|██████████| 446/446 [12:10:51<00:00, 98.32s/it]





# All light curves filtered from the chunk 55
# Processing vari_rrlyrae chunks: 100%|██████████████████████████████████████████████████████████████████████████| 56/56 [1:30:10<00:00, 96.61s/it]
# total light curves filtered in vari_rrlyrae: 114769 / 271779
# 57.77120380897715% of the light curves were deleted with filters:9
#  - L points in each band
#  - average magnitude in band G < M
#  - flux_over_error > 0
# -------------------------------------------------------------------------
# Processing vari_eclipsing_binary chunks: 100%|█████████████████████████████████████████████████████████████████████████████| 446/446 [12:50:13<00:00, 103.62s/it]
# total light curves filtered in vari_eclipsing_binary: 919351 / 2184477
# 57.91436577267694% of the light curves were deleted with filters:
#  - L points in each band
#  - average magnitude in band G < M
#  - flux_over_error > 0












