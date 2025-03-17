import numpy as np
import pandas as pd
import os
import argparse
from astroquery.gaia import Gaia 
from matplotlib import pyplot as plt
        
# main function
if __name__ == "__main__":
    Gaia.login(user='cnavarro', password='Nayeli20*')
    # ["vari_eclipsing_binary" (frequency) -> 2.184.477, "vari_rrlyrae" (pf)-> 271.779]
    for table, period_or_frequency, number_of_lc in [("vari_eclipsing_binary", "frequency", 2184477), ("vari_rrlyrae", "pf", 271779)]: 
        query = f"""
                SELECT * 
                FROM gaiadr3.{table}
                WHERE {period_or_frequency} IS NOT NULL
                """
        job = Gaia.launch_job_async(query, output_file=f"{table}.csv", output_format="csv", dump_to_file=True, verbose=True)
        results = job.get_results()
        print(f"Number of records in {table}:", len(results))
        print(f"Number of lc with null {period_or_frequency} in {table}:", number_of_lc - len(results))
    Gaia.logout()












