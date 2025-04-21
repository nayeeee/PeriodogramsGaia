import os
import pandas as pd
import numpy as np
import pickle as pkl
import sys
sys.path.append("..")
from scripts.periodograms import sort_periodogram, top_frequencies, relative_error, matrix_band
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

def matrix_band(frequencies_ranking, max, top, period, tol,multiples):
    matrix = [ [ [] for i in range(2*max-3) ] for j in range(top) ]
    # para que acepte solo un tol True
    error_tol_true = []
    for i in range(len(frequencies_ranking)):
        for j in range(len(multiples)):
            error = relative_error(1/(frequencies_ranking[i]*multiples[j]), period)
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

# Matrixes of peak of frequencies v/s objetive period (with multiples and submultiples)

def main():
    directory = "../dataset"
    max_mult = 5
    top = 10 
    tol = 1e-2
    multiples = generator_multiples(max_mult)
    valid_lightcurves = pd.read_csv(os.path.join(directory, "valid_lightcurves.csv"))
    for folder_type in ["rrlyrae"]:
        d_folder_type = os.path.join(directory, folder_type)
        # read archive dataset/frequencies_{folder_type}.txt
        freq = pd.read_csv(os.path.join(directory, f"frequencies_{folder_type}.txt"), sep="\n")
        for lc_folder in os.listdir(d_folder_type):
            dict_matrix = {}
            dict_matrix["multiples"] = multiples
            period = valid_lightcurves[(valid_lightcurves['source_id'] == lc_folder) & (valid_lightcurves['type'] == folder_type)]
            directory_lc_folder = os.path.join(d_folder_type, lc_folder)
            directory_periodograms = os.path.join(directory_lc_folder, "periodograms.pkl")
            dict_periodograms = pd.read_pickle(directory_periodograms)
            for band in dict_periodograms.keys():
                per = dict_periodograms[band]
                idx_highest = sort_periodograms(per)
                freq_ranking = top_frequencies(top, idx_highest, freq)
                matrix = matrix_band(freq_ranking, max_mult, top, period, tol, multiples)
                dict_matrix[band] = [freq_ranking, matrix]
            with open(os.path.join(directory_lc_folder, f"error_matrixes{lc_folder}.pkl"), "wb") as handle:
                pkl.dump(dict_matrix, handle, protocol=pkl.HIGHEST_PROTOCOL)

if __name__ == "__main__":
    main()