from astroquery.gaia import Gaia 
import pandas as pd
import sys
import getpass
sys.path.append("..")

id_ecl = 999981777942644864
id_rr = 6042746860650166272

user = input("Username Gaia: ")
password = getpass.getpass("Password Gaia: ")

Gaia.login(user=user, password=password)
# query to get the periodo of the id 
for id, table in [(id_ecl, "vari_eclipsing_binary"), (id_rr, "vari_rrlyrae")]:
    if table == "vari_eclipsing_binary":
        query = f"""
        SELECT frequency
        FROM gaiadr3.{table}
        WHERE source_id = {id}
        """
    else:
        query = f"""
        SELECT pf
        FROM gaiadr3.{table} 
        WHERE source_id = {id}
        """
    result = Gaia.launch_job(query)
    results = result.get_results()
    print(f"results {table}: {results}")
    
# extract pf from dataset/valid_lightcurves.csv
df = pd.read_csv("../dataset/valid_lightcurves.csv")
pf_ecl = df[df['source_id'] == id_ecl]['pf'].values[0]
pf_rr = df[df['source_id'] == id_rr]['pf'].values[0]
# check if the period is the same CHECK
print(f"pf_ecl: {pf_ecl}")
print(f"pf_rr: {pf_rr}")



