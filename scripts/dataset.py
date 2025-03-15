import numpy as np
import pandas as pd
import os
import argparse
from astroquery.gaia import Gaia 
from matplotlib import pyplot as plt
        
# main function
if __name__ == "__main__":
    Gaia.login(user='cnavarro', password='Nayeli20*')
    # ["vari_eclipsing_binary" , "vari_rrlyrae" 271.779]
    for table in ["vari_eclipsing_binary"]: 
        query = f"SELECT * FROM gaiadr3.{table}"
        job = Gaia.launch_job_async(query, dump_to_file=True)
        results = job.get_results()
        print(f"Number of records in {table}:", len(results))
    Gaia.logout()












