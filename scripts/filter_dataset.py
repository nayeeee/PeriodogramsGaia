# filter dataset

# 1.- Extract N examples or all:
# * where pf or frequency is not null 
# * L points in each band 
# * average magnitude in band G < M
# * 

import pandas as pd
import os
from tqdm import tqdm
import numpy as np
import math
import sys
sys.path.append("..")
from astroquery.gaia import Gaia

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
    mask = mask_g | mask_bp | mask_rp

    name = lc.source_id[0]
    
    lc_1 = lc.loc[mask]

    common_columns = ['solution_id', 'source_id', 'transit_id', 'g_transit_time']
    columns_g  = ['g_transit_flux', 'g_transit_flux_error', 'g_transit_flux_over_error', 'g_transit_mag', 'variability_flag_g_reject', 'g_other_flags']
    columns_bp = ['bp_obs_time', 'bp_flux', 'bp_flux_error', 'bp_flux_over_error', 'bp_mag', 'variability_flag_bp_reject', 'bp_other_flags']
    columns_rp = ['rp_obs_time', 'rp_flux', 'rp_flux_error', 'rp_flux_over_error', 'rp_mag', 'variability_flag_rp_reject', 'rp_other_flags']

    lc_1_g = lc_1[common_columns + columns_g]
    lc_1_bp = lc_1[common_columns + columns_bp]
    lc_1_rp = lc_1[common_columns + columns_rp]
    
    points_G = lc_1_g.shape[0]
    points_BP = lc_1_bp.shape[0]
    points_RP = lc_1_rp.shape[0]
    mag_mean_G = np.mean(lc_1_g["g_transit_mag"])

    # Ver si cumple las condiciones de puntos en cada banda, mag promedio en la banda G y que no este repetido. Ademas que la mascara no sea vacia para alguna banda
    if ((points_BP >= L) & (points_G >= L) & (points_RP >= L) & (mag_mean_G < M)):
        # Creo carpeta para cada lc
        parent_dir = os.path.join(path, type_star)
        path_lc = os.path.join(parent_dir, str(name))
        # print(parent_dir + " -> " + path)
        os.mkdir(path_lc) 
        path_lc = os.path.join(path_lc, str(name)+'.pkl')
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
    valid_csv = os.path.join(parent_dir, "valid_lightcurves.csv")
    if not os.path.exists(valid_csv):
        with open(valid_csv, 'w') as f:
            f.write("source_id,pf,type\n")
    
    # Create CSV for invalid light curves
    invalid_csv = os.path.join(parent_dir, "invalid_lightcurves.csv")
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
    
    # reads csv files with the results of the query
    # ["vari_eclipsing_binary", "vari_rrlyrae"]
    for table in ["vari_rrlyrae"]:
        valid_lc = 0
        not_valid_lc = 0
        # load results
        print(f"Loading results in {table}.csv...")
        path_results = os.path.join(f"{table}.csv")
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
                    pf = 1/source_info['frequency'] if table == "vari_eclipsing_binary" else source_info['pf']
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
                    f.write('\n'.join(valid_results) + '\n')
            
            if invalid_results:
                with open(invalid_csv, 'a') as f:
                    f.write('\n'.join(invalid_results) + '\n')
            print(f"All light curves filtered from the chunk {i}")
            
        print(f"total light curves filtered in {table}: {valid_lc} / {len(ids)}")
        print(f"{(len(ids)-valid_lc)*100/len(ids)}% of the light curves were deleted with filters:\n - L points in each band \n - average magnitude in band G < M")

# OUTPUT:
# Processing vari_rrlyrae chunks: 100%|████████████████████████████████████████████████████████████████████████████Processing vari_rrlyrae chunks: 100%|███████████████████████████████████████████████████████████████████████████████████████████| 37/37 [2:35:00<00:00, 251.37s/it]
# total light curves filtered in vari_rrlyrae: 81515 / 177357
# 54.03902862587888% of the light curves were deleted with filters:
#  - L points in each band
#  - average magnitude in band G < M





















