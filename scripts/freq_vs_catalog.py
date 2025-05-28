import os
import pickle
import pandas as pd
import matplotlib.pyplot as plt
from tqdm import tqdm
import sys
import numpy as np
sys.path.append('..')

def list_periods(type_lc, list_lc):
    directory = os.path.join('dataset', type_lc)
    dict_periods = {
        'g': [],
        'bp': [],
        'rp': [],
        'multiband': []
    }
    for lc_folder in tqdm(list_lc, desc=f"Extracting periods for {type_lc}"):
        d_lc_folder = os.path.join(directory, lc_folder)
        dict_matrixes = pd.read_pickle(d_lc_folder + '/error_matrixes_'+ lc_folder + '.pkl')
        for band in ['g', 'bp', 'rp', 'multiband']:
            real_period = dict_matrixes['real_period']
            candidate_period = dict_matrixes[band][1][0]
            multiple_period = dict_matrixes[band][1][1] 
            if candidate_period != None and multiple_period != None:
                real_period_candidate = candidate_period / multiple_period
                dict_periods[band].append((real_period, real_period_candidate))
            
    return dict_periods

if __name__ == "__main__":
    directory = "dataset"
    results_dir = "results"
    for folder_type in ["eclipsing_binary"]:
        # directory of the type
        d_folder_type = os.path.join(directory, folder_type)
        # list of the light curves
        list_lc = os.listdir(d_folder_type)
        # list of the periods 
        # {'g': [(real_period, candidate_period), ...], 
        # 'bp': [(real_period, candidate_period), ...], 
        # 'rp': [(real_period, candidate_period), ...], 
        # 'multiband': [(real_period, candidate_period), ...]}
        dict_periods = list_periods(folder_type, list_lc)
        # check if the file exists
        if os.path.exists(os.path.join(os.path.join(directory, results_dir), f'periods_{folder_type}.pkl')):
            # delete the file
            os.remove(os.path.join(os.path.join(directory, results_dir), f'periods_{folder_type}.pkl'))
        
        # save the periods
        with open(os.path.join(os.path.join(directory, results_dir), f'periods_{folder_type}.pkl'), 'wb') as f:
            pickle.dump(dict_periods, f)
        