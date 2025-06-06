import os
import pickle
import pandas as pd
import matplotlib.pyplot as plt
from tqdm import tqdm
import sys
import numpy as np
sys.path.append('..')

def scatter_plot_bands(df, folder_type, 
                               figsize=(16, 14), alpha=0.15, s=10):
    """
    Function to create 4 scatter plots (2x2) from a dictionary of bands
    
    Parameters:
    -----------
    df : pd.DataFrame
        DataFrame with columns: id, real_frequency, best_frequency_g, best_frequency_bp, best_frequency_rp, best_frequency_multiband
    folder_type : str
        Type of folder to save the file
    figsize : tuple
        Size of the complete figure (width, height)
    alpha : float
        Transparency of the points (0-1)
    s : int
        Size of the points
    """
    # Define the bands and their colors
    bandas = ['g', 'bp', 'rp', 'multiband']
    colores = ['green', 'blue', 'red', 'purple']
    titulos_bandas = ['G Band', 'BP Band', 'RP Band', 'Multiband']
    
    # Create the results directory if it doesn't exist
    directory = "dataset"
    results_dir = "results"
    
    # Create the figure with 4 subplots in 2x2 disposition
    fig, axes = plt.subplots(2, 2, figsize=figsize)
    axes = axes.flatten()  # Flatten to facilitate iteration
    
    # Create each scatter plot
    for i, (banda, color, titulo_banda) in enumerate(zip(bandas, colores, titulos_bandas)):
        ax = axes[i]
        # Extract x (real_period) and y (candidate_period) from the tuples
        x = df['real_frequency'].values
        y = df[f'best_frequency_{banda}'].values
            
        # Create the scatter plot
        ax.scatter(x, y, color=color, alpha=alpha, s=s, 
                  edgecolors='white', linewidth=0.5)
            
        # Calculate the limits for the x=y line
        if len(x) > 0 and len(y) > 0:
            min_val = min(min(x), min(y))
            # print(f"min_val x: {min(x)}")
            # print(f"min_val y: {min(y)}")
            max_val = max(max(x), max(y))
            # print(f"max_val x: {max(x)}")
            # print(f"max_val y: {max(y)}")
                
            # Add the dashed x=y line
            ax.plot([min_val, max_val], [min_val, max_val], 
                   'k--', alpha=0.8, linewidth=2)
            
        # Calculate the statistics
        if len(x) > 0:
            correlacion = np.corrcoef(x, y)[0, 1] if len(x) > 1 else 0
            n_puntos = len(x)
                
            # Add the text with the statistics
            stats_text = f'r = {correlacion:.3f}\nN = {n_puntos}'
            ax.text(0.05, 0.95, stats_text, transform=ax.transAxes,
                   bbox=dict(boxstyle='round', facecolor='white', alpha=0.8),
                   verticalalignment='top', fontsize=10)

        
        # Configure each subplot
        ax.set_title(titulo_banda, fontsize=14, pad=10)
        ax.set_xlabel('Real Frequency', fontsize=12)
        ax.set_ylabel('Periodogram Peak Frequency', fontsize=12)
        ax.grid(True, alpha=0.3)
        
        # Make the axes have the same scale for better visualization of x=y
        # if banda in data_dict and len(data_dict[banda]) > 0:
            # ax.set_aspect('equal', adjustable='box')
        ax.set_xlim([0, 6])
    
    # Global title of the figure
    fig.suptitle(f'Period Recovery Analysis - {folder_type}', 
                fontsize=18, fontweight='bold', y=0.98)
    
    # Adjust the layout
    plt.tight_layout()
    plt.subplots_adjust(top=0.93)  # Space for the global title
    
    # Save the figure
    filename = f'scatter_periods_{folder_type}.png'
    filepath = os.path.join(os.path.join(directory, results_dir), filename)
    # verify if the file exists
    if os.path.exists(filepath):
        # delete the file
        os.remove(filepath)
    # save the figure   
    plt.savefig(filepath, dpi=300, bbox_inches='tight')
    plt.close()
    
    print(f"Periods saved in: {filepath}")
    
if __name__ == "__main__":
    directory = "dataset"
    results_dir = "results"
    for folder_type in ["rrlyrae"]: 
        # load the periods
        df = pd.read_csv(f'dataset/frequencies_data_{folder_type}.csv')
        # plot the periods
        scatter_plot_bands(df, folder_type)