import os
import pandas as pd
import numpy as np
import pickle as pkl
import sys
import ray
from tqdm import tqdm
sys.path.append("..")

cpus_per_task = 1  # CPUs per task
total_cpus = 2    # Total CPUs available

# size max-1 + max-2
def generator_multiples(max):
    mult = np.concatenate([np.arange(1, max, 1), # multiples
                                1./np.arange(2, max, 1)]) # submultiples
    return mult

def sort_periodogram(per):
    local_maxima = np.where((per[1:-1] > per[:-2]) & (per[1:-1] > per[2:]))[0] + 1
    idx_highest = local_maxima[np.argsort(per[local_maxima])[::-1]]
    return idx_highest

def top_frequencies(top, idx_highest, freq):
    frequencies = [freq[i] for i in idx_highest]
    return frequencies[:top]

def relative_error(observed, actual):
    return np.absolute((observed - actual)/actual)

def matrix_band(frequencies_ranking, max, top, period, tol, multiples):
    matrix = [ [ [] for i in range(2 * max - 3) ] for j in range(top) ]
    # para que acepte solo un tol True
    error_tol_true = []
    for i in range(len(frequencies_ranking)):
        for j in range(len(multiples)):
            error = relative_error((1 / frequencies_ranking[i]) * multiples[j], period)
            if (error < tol):
                if len(error_tol_true) == 0:
                    error_tol_true = [error, i, j]
                    tol_bool = True
                else:
                    if error_tol_true[0] >  error:
                        matrix[error_tol_true[1]][error_tol_true[2]] = [error_tol_true[0], False]
                        error_tol_true = [error, i, j]
                        tol_bool = True
                    else:
                        tol_bool = False
                    
            else:
                tol_bool = False
            matrix[i][j] = [error, tol_bool]
    return matrix

@ray.remote(num_cpus=cpus_per_task)
def matrix_all_bands(multiples, valid_lightcurves, lc_folder, folder_type, d_folder_type, freq):
    dict_matrix = {}
    dict_matrix["multiples"] = multiples
    period = valid_lightcurves[(valid_lightcurves['source_id'] == int(lc_folder)) & (valid_lightcurves['type'] == folder_type)]['pf'].values[0]
    directory_lc_folder = os.path.join(d_folder_type, lc_folder)
    directory_periodograms = os.path.join(directory_lc_folder, "periodograms.pkl")
    dict_periodograms = pd.read_pickle(directory_periodograms)
    for band in dict_periodograms.keys():
        per = dict_periodograms[band]
        idx_highest = sort_periodogram(per)
        freq_ranking = top_frequencies(top, idx_highest, freq)
        matrix = matrix_band(freq_ranking, max_mult, top, period, tol, multiples)
        dict_matrix[band] = [freq_ranking, matrix]
    return dict_matrix, directory_lc_folder, lc_folder
# Matrixes of peak of frequencies v/s objetive period (with multiples and submultiples)

if __name__ == "__main__":
    concurrent_tasks = total_cpus // cpus_per_task  # = 16 tasks simultaneously
    batch_size = concurrent_tasks * 2  # = 32 to have two rounds of tasks
    print(f"setting batch size to {batch_size}")

    print("Initializing Ray")
    ray.init(num_cpus=total_cpus)
    print("Ray initialized")
    
    directory = "dataset10"
    max_mult = 5
    top = 10 
    tol = 1e-1
    print("Generating multiples and submultiples")
    # set multiples and submultiples
    multiples = generator_multiples(max_mult)
    print("reading frequencies")
    # read frequencies
    with open(os.path.join(directory, "frequencies.txt"), 'r') as f:
        freq = np.array([float(line.strip()) for line in f])
    print("reading valid light curves")
    # read valid light curves
    valid_lightcurves = pd.read_csv(os.path.join(directory, f"valid_lightcurves.csv"))
    
    for folder_type in ["eclipsing_binary", "rrlyrae"]:
        print(f"Matrixes of peak of frequencies v/s objetive period (with multiples and submultiples) for {folder_type}")
        # directory of the type
        d_folder_type = os.path.join(directory, folder_type)
        # list of the light curves
        list_lc_without_filters = os.listdir(d_folder_type)
        """
        print(f"Reading dataset10/with_warnings_{folder_type}.csv")
        # read the file dataset10/with_warnings_{type_lc}.csv
        warnings_lc = pd.read_csv(os.path.join(directory, f"with_warnings_{folder_type}.csv"))
        warnings_lc_source_id = warnings_lc['source_id'].astype(str).tolist()
        
        print(f"Reading dataset10/without_points_{folder_type}.csv")
        # read the file dataset10/without_points_{type_lc}.csv
        without_points = pd.read_csv(os.path.join(directory, f"without_points_{folder_type}.csv"))
        without_points_source_id = without_points['source_id'].astype(str).tolist()

        print(f"Light curves before discarding: {len(list_lc_without_filters)}")
        print(f"Discarding {len(warnings_lc_source_id)} light curves with warnings and {len(without_points_source_id)} light curves without points")
        # discard warnings_lc_source_id and without_points_source_id from list_lc
        list_lc = [lc for lc in list_lc_without_filters if lc not in warnings_lc_source_id and lc not in without_points_source_id]
        print(f"Light curves after discarding: {len(list_lc)}")
        """
        # without filters TEST
        list_lc = list_lc_without_filters
        print(f"calculating matrixes of peak of frequencies v/s objetive period (with multiples and submultiples) for {len(list_lc)} light curves")
        for i in tqdm(range(0, len(list_lc), batch_size), desc=f"Calculating matrixes for {folder_type}"):
            # get the batch
            batch = list_lc[i:i+batch_size]
            # calculate matrixes  
            results = ray.get([matrix_all_bands.remote(multiples, valid_lightcurves, lc_folder, folder_type, d_folder_type, freq) for lc_folder in batch])
            
            # save the results
            for result in results:
                dict_matrix, directory_lc_folder, lc_folder = result
                with open(os.path.join(directory_lc_folder, f"error_matrixes_{lc_folder}.pkl"), "wb") as handle:
                    pkl.dump(dict_matrix, handle, protocol=pkl.HIGHEST_PROTOCOL)
