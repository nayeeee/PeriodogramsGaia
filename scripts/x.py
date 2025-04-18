# read a file of the light curve in the folder dataset/eclipsing_binary/
import sys 
import os
import pandas as pd
import numpy as np
import pickle
import ray
from functools import partial
from astropy.timeseries import LombScargle


sys.path.append("..")



# Leer el CSV
# lc = pd.read_pickle('dataset/eclipsing_binary/5277229516350094592/5277229516350094592.pkl')
periodograms = pd.read_pickle('dataset/periodograms_4050275694921784704.pkl')
x = 0
for band in ['g', 'bp', 'rp']:
    for key in periodograms[band]:
        if key == np.float64(np.inf) or key == np.float64(np.nan) or key == np.float64(0):
            x += 1
    print(f"number of inf, nan or 0 in band {band}: {x}")
    x = 0









