import os
from pathlib import Path
import sys

sys.path.append("..")

def find_missing_periodograms(base_dir="dataset", type_dir="rrlyrae"):
    """
    Search for folders that do not contain periodograms.pkl
    
    Args:
        base_dir (str): Base directory where to search
        type_dir (str): Subdirectory of the type of star
    
    Returns:
        list: List of folders without periodograms.pkl
    """
    # Build the full path
    search_dir = Path(base_dir) / type_dir
    
    # List to store folders without periodograms.pkl
    missing_periodograms = []
    
    # Verify that the directory exists
    if not search_dir.exists():
        print(f"The directory {search_dir} does not exist!")
        return missing_periodograms
    
    # Iterate through all folders
    for folder in search_dir.iterdir():
        if folder.is_dir():  # Ensure it is a directory
            periodogram_file = folder / "periodograms.pkl"
            if not periodogram_file.exists():
                missing_periodograms.append(folder.name)
    
    return missing_periodograms

if __name__ == "__main__":
    # Star type to verify
    star_type = "eclipsing_binary"
    print(f"\nSearching in {star_type}...")
    missing = find_missing_periodograms(type_dir=star_type)
        
    # Show results
    if missing:
        print(f"Found {len(missing)} folders without periodograms.pkl:")
        for folder in missing:
            print(f"  - {folder}")
            
        # Save the list in a file
        output_file = f"missing_periodograms_{star_type}.txt"
        with open(output_file, "w") as f:
            f.write("\n".join(missing))
        print(f"\nList saved in {output_file}")
    else:
        print("All folders have periodograms.pkl")