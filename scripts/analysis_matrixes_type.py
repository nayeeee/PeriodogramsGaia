import os
import pandas as pd
import sys
from tqdm import tqdm
import pickle

sys.path.append("..")

"""
- do analysis for each type of light curve (ECL and RR) and band:
  - make a count, how many the tol=True (candidate) is in the first position
  - how many dont have any good candidate
  - how many the candidate coincides in another position (2,3,5,...)
  - check if it is worth the multiband, that if the best candidate rises in the ranking in the multiband 
  compared to the other bands
"""

def list_matrixes(type_lc, list_lc):
    directory = os.path.join('dataset10', type_lc)
    dict_matrixes = {
        'g': [],
        'bp': [],
        'rp': [],
        'multiband': []
    }
    dict_cont = {
        'g': 0,
        'bp': 0,
        'rp': 0,
        'multiband': 0
    }
    
    for lc_folder in tqdm(list_lc, desc=f"Reading matrixes for {type_lc}"):
        d_lc_folder = os.path.join(directory, lc_folder)
        matrixes = pd.read_pickle(d_lc_folder + '/error_matrixes_'+ lc_folder + '.pkl')
        for band in ['g', 'bp', 'rp', 'multiband']:
            dict_matrixes[band].append(matrixes[band][1])
            dict_cont[band] += 1

    return dict_cont, dict_matrixes

def calculate_matrix_cont(top, max_mult, list_matrixes_band):
    matrix_cont = [ [ [] for i in range(2*max_mult-3) ] for j in range(top) ]
    for i in tqdm(range(top), desc=f"Calculating matrix for top"):
        for j in tqdm(range(2*max_mult-3), desc=f"Calculating matrix for max_mult"):
            matrix_cont[i][j] = 0
            for lc in tqdm(list_matrixes_band, desc=f"Calculating matrix for lc"):
                if lc[i][j][1] == True:
                    matrix_cont[i][j] += 1
    return matrix_cont

def write_matrix_cont(matrix, top, max_mult, type_lc, band, num_lc, output_file):
    with open(output_file, 'a') as f:  # 'a' to append to the file
        f.write(f'\nCounter where the tolerance is True\ntype:{type_lc} band: {band}\n')
        cont_with_tol = 0
        for i in range(top):
            f.write(f'freq ranking {i+1}  ')
            for j in range(2*max_mult-3):
                porcentage = matrix[i][j]*100/num_lc
                f.write('{:.2f}% '.format(porcentage))
                cont_with_tol += matrix[i][j]
            f.write('\n')
        f.write('{:.2f}% of the light curves do not have tolerance True\n\n'.format((num_lc-cont_with_tol)*100/num_lc))

if __name__ == "__main__":
    top = 10
    max_mult = 5
    directory = "dataset10"
    print("Creating results/matrixes folder")
    # verify if the 'results' exists
    folder_results = 'dataset10/results'
    if not os.path.exists(folder_results):
        os.makedirs(folder_results)
            
    folder_results_matrixes = os.path.join(folder_results, 'matrixes')
    if not os.path.exists(folder_results_matrixes):
        os.makedirs(folder_results_matrixes)
        
    print(f"Reading dataset10/valid_lightcurves.csv")
    # read valid light curves
    valid_lightcurves = pd.read_csv(os.path.join(directory, f"valid_lightcurves.csv"))
    for type_lc in ['eclipsing_binary', 'rrlyrae']:
        # Path to the output file
        output_file = os.path.join(folder_results_matrixes, f'output_{type_lc}.txt')
        
        # Delete the file if it exists to start fresh
        if os.path.exists(output_file):
            os.remove(output_file)
        """
        print(f"Reading dataset10/with_warnings_{type_lc}.csv")
        # read the file dataset10/with_warnings_{type_lc}.csv
        warnings_lc = pd.read_csv(os.path.join(directory, f"with_warnings_{type_lc}.csv"))
        warnings_lc_source_id = warnings_lc['source_id'].astype(str).tolist()
        
        print(f"Reading dataset10/without_points_{type_lc}.csv")
        # read the file dataset10/without_points_{type_lc}.csv
        without_points = pd.read_csv(os.path.join(directory, f"without_points_{type_lc}.csv"))
        without_points_source_id = without_points['source_id'].astype(str).tolist()
        
        list_lc_without_filters = os.listdir(os.path.join(directory, type_lc))
        print(f"Light curves before discarding: {len(list_lc_without_filters)}")
        print(f"Discarding {len(warnings_lc_source_id)} light curves with warnings and {len(without_points_source_id)} light curves without points")
        # discard warnings_lc_source_id and without_points_source_id from list_lc
        list_lc = [lc for lc in list_lc_without_filters if lc not in warnings_lc_source_id and lc not in without_points_source_id]
        print(f"Light curves after discarding: {len(list_lc)}")
        """
        list_lc = os.listdir(os.path.join(directory, type_lc))
        print(f"Reading matrixes for {type_lc}")
        dict_cont, dict_matrixes = list_matrixes(type_lc, list_lc)

        for band in ['g', 'bp', 'rp', 'multiband']:
            list_matrixes_band = dict_matrixes[band]
            cont_lc = dict_cont[band]

            print(f"Calculating matrix for {band} band, type: {type_lc}")
            matrix_cont = calculate_matrix_cont(top, max_mult, list_matrixes_band)
            # pending save cont_lc
            # save the matrix_cont
            with open(os.path.join(folder_results_matrixes, f"matrix_cont_{type_lc}_{band}.pkl"), 'wb') as f:
                pickle.dump(matrix_cont, f)
            # write the matrix_cont
            write_matrix_cont(matrix_cont, top, max_mult, type_lc, band, cont_lc, output_file)
