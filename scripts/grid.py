# Calculate the grid of frequencies for the light curves
# Calculate minimum and maximum frequencies per type of star, using all tables

import pandas as pd

def min_max_freq(data_eclipsing_binary, data_rrlyrae):
    types = ["eclipsing_binary", "rrlyrae"]
    grid = pd.DataFrame(columns=['type', 'low-frequency', 'high-frequency'])
    for i, name_type in enumerate(types):
        if name_type == "eclipsing_binary":
            # extract columns frequency from data_eclipsing_binary
            freq = data_eclipsing_binary["frequency"]
            # pf = 1/freq
        else:
            pf = data_rrlyrae["pf"]
            freq = 1/pf
        # add row to grid
        grid.loc[len(grid)] = [name_type, min(freq), max(freq)]
    return grid

# Read the file with the light curves
data_eclipsing_binary = pd.read_csv(f"dataset/vari_eclipsing_binary.csv")
data_rrlyrae = pd.read_csv(f"dataset/vari_rrlyrae.csv")
grid = min_max_freq(data_eclipsing_binary, data_rrlyrae)
# save grid to csv in dataset folder
grid.to_csv(f"dataset/grid.csv", index=True)
print(f"Grid:\n{grid}")
print(f"Grid saved to dataset/grid.csv")

# OUTPUT:
# Grid:
#                  low-frecuency high-frequency
# eclipsing_binary      0.200003     678.890625
# rrlyrae               0.201076        0.99939
# Grid saved to dataset/grid.csv