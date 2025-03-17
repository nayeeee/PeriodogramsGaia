# filter dataset

# 1.- Extract N examples or all:
# * where pf or frequency is not null 
# * L points in each band 
# * average magnitude in band G < M
# * 

# from astropy.table import Table

# ruta_archivo = r"C:\Users\nayel\OneDrive\Documentos\PeriodogramsGaia\vari_rrlyrae-result.vot.gz"
# tabla = Table.read(ruta_archivo, format="votable")
# print(tabla.columns)

# TableColumns names=('solution_id','SOURCE_ID','pf','pf_error','p1_o','p1_o_error','epoch_g','epoch_g_error','epoch_bp','epoch_bp_error','epoch_rp','epoch_rp_error','epoch_rv','epoch_rv_error','int_average_g','int_average_g_error','int_average_bp','int_average_bp_error','int_average_rp','int_average_rp_error','average_rv','average_rv_error','peak_to_peak_g','peak_to_peak_g_error','peak_to_peak_bp','peak_to_peak_bp_error','peak_to_peak_rp','peak_to_peak_rp_error','peak_to_peak_rv','peak_to_peak_rv_error','metallicity','metallicity_error','r21_g','r21_g_error','r31_g','r31_g_error','phi21_g','phi21_g_error','phi31_g','phi31_g_error','num_clean_epochs_g','num_clean_epochs_bp','num_clean_epochs_rp','num_clean_epochs_rv','zp_mag_g','zp_mag_bp','zp_mag_rp','num_harmonics_for_p1_g','num_harmonics_for_p1_bp','num_harmonics_for_p1_rp','num_harmonics_for_p1_rv','reference_time_g','reference_time_bp','reference_time_rp','reference_time_rv','fund_freq1','fund_freq1_error','fund_freq2','fund_freq2_error','fund_freq1_harmonic_ampl_g','fund_freq1_harmonic_ampl_g_error','fund_freq1_harmonic_phase_g','fund_freq1_harmonic_phase_g_error','fund_freq1_harmonic_ampl_bp','fund_freq1_harmonic_ampl_bp_error','fund_freq1_harmonic_phase_bp','fund_freq1_harmonic_phase_bp_error','fund_freq1_harmonic_ampl_rp','fund_freq1_harmonic_ampl_rp_error','fund_freq1_harmonic_phase_rp','fund_freq1_harmonic_phase_rp_error','fund_freq1_harmonic_ampl_rv','fund_freq1_harmonic_ampl_rv_error','fund_freq1_harmonic_phase_rv','fund_freq1_harmonic_phase_rv_error','best_classification','g_absorption','g_absorption_error')


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
    # Ver que la mascara no de vacia para time, flux y flux_err
    # print("lc columns", lc.columns)
    # print("LCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCC", lc.iloc[0])
    # print(0/0)
    mask_g = lc["variability_flag_g_reject"]=="false"
    mask_bp = lc["variability_flag_bp_reject"]=="false"
    mask_rp = lc["variability_flag_rp_reject"]=="false"
    mask = mask_g | mask_bp | mask_rp

    name = lc.source_id[0]
    
    lc_1 = lc.loc[mask]

    bands = ['G', 'BP', 'RP']
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

if __name__ == "__main__":
    
    CHUNK_SIZE = 4900
    L = 10
    M = 18
    data_global = pd.DataFrame()
    
    print(f"Creating dataset folder...")
    create_folder_dataset()
    # reads csv files with the results of the query
    # ["vari_eclipsing_binary", "vari_rrlyrae"]
    for table in ["vari_eclipsing_binary", "vari_rrlyrae"]:
        valid_lc = []
        not_valid_lc = []
        print(f"Loading results in {table}.csv...")
        path_results = os.path.join(f"{table}.csv")
        results = pd.read_csv(path_results)
        print(f"Results loaded in {table}.csv")
        ids = results["source_id"].tolist() 
        
        # extract per chunk of 4900 (https://www-cosmos-esa-int.translate.goog/web/gaia-users/archive/datalink-products?_x_tr_sl=en&_x_tr_tl=es&_x_tr_hl=es&_x_tr_pto=tc#datalink_jntb_get_above_lim)
        print(f"Chunks: {math.ceil(len(ids) / CHUNK_SIZE)} with CHUNK_SIZE = {CHUNK_SIZE}")
        ids_chunks = list(chunks(ids, CHUNK_SIZE))
        datalink_all = []
        
        print(f"Extracting light curves from Gaia DR3...")
        # extract light curves from Gaia DR3
        for i, chunk in enumerate(ids_chunks):
            datalink = Gaia.load_data(ids=chunk, 
                            data_release='Gaia DR3', 
                            retrieval_type='EPOCH_PHOTOMETRY', 
                            format='csv')
            datalink_all.append(datalink)
        print(f"Light curves extracted from Gaia DR3")
        # merge chunks into one single object (python dictionary)
        print(f"Merging light curves...")
        datalink_out = datalink_all[0]
        for inp_dict in datalink_all[1:]:
            datalink_out.update(inp_dict)
        keys = list(datalink_out.keys())
        print(f'* The merged dictionary contains {len(keys)} elements of table {table}') 
        print(f"Filtering light curves...")
        for _, (key, value) in enumerate(datalink_out.items()):
            lc = value[0].to_pandas()
            is_valid, name = verification_lc(lc, "dataset", table[5:], L, M)
            if is_valid:
                valid_lc.append(name)
        print(f"Light curves filtered")
        print(f"total light curves filtered in {table}: {len(valid_lc)} / {len(ids)}")
        print(f"{(len(ids)-len(valid_lc))*100/len(ids)}% of the light curves were deleted with filters:\n - L points in each band \n - average magnitude in band G < M")

        # add ids, pf and type of star to data_global
        print("Creating data_global: dataFrame with pf, type of star and source_id")
        
        # add a column with period pf in vari_eclipsing_binary
        if table == "vari_eclipsing_binary":
            results["pf"] = 1/results["frequency"]
        
        # add a column with the type of star in results
        results["type"] = table[5:]
        
        # select in results the rows where source_id is in valid_lc
        results = results[results["source_id"].isin(valid_lc)]
        
        # select the columns source_id, pf and type
        columns = ["source_id", "pf", "type"]
        results_filtered = results[columns]
        
        data_global = pd.concat([data_global, results_filtered])

    # save data_global
    path_data_global = os.path.join("dataset", "data_global.csv")
    data_global.to_csv(path_data_global, index=False)






















