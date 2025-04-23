# read a file of the light curve in the folder dataset/eclipsing_binary/
import sys 
import os
import pandas as pd
import numpy as np
import pickle
import ray
from functools import partial
from astropy.timeseries import LombScargle
from tqdm import tqdm

sys.path.append("..")



directory = 'dataset'
folder_type = 'rrlyrae'
max_mult = 5

# list of the light curves
list_lc_without_filters = os.listdir(os.path.join(directory, folder_type))
print(f"Reading dataset/with_warnings_{folder_type}.csv")
# read the file dataset/with_warnings_{type_lc}.csv
warnings_lc = pd.read_csv(os.path.join(directory, f"with_warnings_{folder_type}.csv"))
warnings_lc_source_id = warnings_lc['source_id'].astype(str).tolist()

print(f"Reading dataset/without_points_{folder_type}.csv")
# read the file dataset/without_points_{type_lc}.csv
without_points = pd.read_csv(os.path.join(directory, f"without_points_{folder_type}.csv"))
without_points_source_id = without_points['source_id'].astype(str).tolist()

print(f"Light curves before discarding: {len(list_lc_without_filters)}")
print(f"Discarding {len(warnings_lc_source_id)} light curves with warnings and {len(without_points_source_id)} light curves without points")
# discard warnings_lc_source_id and without_points_source_id from list_lc
list_lc = [lc for lc in list_lc_without_filters if lc not in warnings_lc_source_id and lc not in without_points_source_id]
print(f"Light curves after discarding: {len(list_lc)}")

true_in_matrix = 0
for lc_name in tqdm(list_lc, desc="Processing light curves"):
    # read the file directory/lc/error_matrixes_lc.pkl
    with open(os.path.join(directory, folder_type, lc_name, f"error_matrixes_{lc_name}.pkl"), 'rb') as f:
        matrix = pickle.load(f)
    for i in range(10):
        for j in range(2*max_mult-3):
            matrix_band = matrix['g'][1]
            if matrix_band[i][j][1] == True:
                true_in_matrix += 1
print(true_in_matrix)










