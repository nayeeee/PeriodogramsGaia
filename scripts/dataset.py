
import os
from astroquery.gaia import Gaia 
import getpass
import sys
sys.path.append("..")

# STEP 1: Get the data from Gaia

# verify that the folder "datasets" exists
if not os.path.exists("dataset"):
        os.makedirs("dataset")
        
# main function
if __name__ == "__main__":
        # [("vari_eclipsing_binary", "frequency", 2184477), ("vari_rrlyrae", "pf", 271779)]
        for table, period_or_frequency, number_of_lc in [("vari_eclipsing_binary", "frequency", 2184477)]: 
                user = input("Username Gaia: ")
                password = getpass.getpass("Password Gaia: ")
                
                Gaia.login(user=user, password=password)
                if table == "vari_eclipsing_binary":
                        query = f"""
                                SELECT * 
                                FROM gaiadr3.{table}
                                WHERE {period_or_frequency} IS NOT NULL  
                                """
                # vari_rrlyrae
                else:
                        query = f"""
                                SELECT * 
                                FROM gaiadr3.{table}
                                WHERE {period_or_frequency} IS NOT NULL OR "p1_o" IS NOT NULL
                                """
                job = Gaia.launch_job_async(query, output_file=f"dataset/{table}.csv", output_format="csv", dump_to_file=True, verbose=True)
                results = job.get_results()
                print(f"Number of records in {table}:", len(results))
                print(f"Number of lc with period null in {table}:", number_of_lc - len(results))
                Gaia.logout()
        
## OUTPUT:
# Saving results to: vari_eclipsing_binary.csv
# Number of records in vari_eclipsing_binary: 2184477
# Number of lc with null frequency in vari_eclipsing_binary: 0
# ----------------------------------------------
# Saving results to: vari_rrlyrae.csv
# Number of records in vari_rrlyrae: 271779
# Number of lc with null pf in vari_rrlyrae: 0













