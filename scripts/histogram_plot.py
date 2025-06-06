import os
import pickle
import numpy as np
import matplotlib.pyplot as plt
import sys
import pandas as pd
from tqdm import tqdm
sys.path.append('..')

# bin = 100 o 1000
def plot_histogram(df, folder_type,
                      bins=100, alpha=0.7, figsize=(16, 12),
                      mostrar_estadisticas=True, mostrar_curva_normal=False):
    """
    Función para crear 4 histogramas (2x2) desde un diccionario de bandas
    
    Parámetros:
    -----------
    df : pd.DataFrame
        DataFrame con las columnas: id, real_frequency, best_frequency_g, best_frequency_bp, best_frequency_rp, best_frequency_multiband
    type_lc : str
        Tipo de curva de luz para el título global
    folder_type : str
        Tipo de carpeta para guardar el archivo
    bins : int
        Número de bins para cada histograma
    alpha : float
        Transparencia de las barras (0-1)
    figsize : tuple
        Tamaño de la figura completa (ancho, alto)
    mostrar_estadisticas : bool
        Si mostrar estadísticas descriptivas en cada gráfico
    mostrar_curva_normal : bool
        Si superponer una curva normal teórica en cada histograma
    """
    # Definir las bandas y sus colores
    bandas = ['g', 'bp', 'rp', 'multiband']
    colores = ['green', 'blue', 'red', 'purple']
    titulos_bandas = ['G Band', 'BP Band', 'RP Band', 'Multiband']
    
    # Crear directorio de resultados si no existe
    directory = "dataset"
    results_dir = "results"
    directory_results = os.path.join(directory,results_dir)
    
    # Crear la figura con 4 subplots en disposición 2x2
    fig, axes = plt.subplots(2, 2, figsize=figsize)
    axes = axes.flatten()  # Aplanar para facilitar la iteración
    
    # Crear cada histograma
    for i, (band, color, title_band) in enumerate(zip(bandas, colores, titulos_bandas)):
        ax = axes[i]
        
        # Verificar si la banda existe en el diccionario y tiene datos
        datos = df[f'best_frequency_{band}'].values
            
        # Crear el histograma
        n, bins_edges, patches = ax.hist(datos, bins=bins, alpha=alpha, 
                                           color=color, edgecolor='black', 
                                           density=mostrar_curva_normal)
        ax.set_yscale('log')
        
            
        # Si se solicita, superponer una curva normal
        if mostrar_curva_normal and len(datos) > 1:
            media = np.mean(datos)
            std = np.std(datos)
            if std > 0:  # Evitar división por cero
                x = np.linspace(datos.min(), datos.max(), 100)
                curva_normal = (1/(std * np.sqrt(2 * np.pi))) * np.exp(-0.5 * ((x - media) / std) ** 2)
                ax.plot(x, curva_normal, 'r-', linewidth=2, label='Normal Teórica')
                ax.legend()
            
        # Añadir estadísticas al gráfico si se solicita
        if mostrar_estadisticas and len(datos) > 0:
            media = np.mean(datos)
            mediana = np.median(datos)
            std = np.std(datos)
            n_datos = len(datos)
                
            # Crear texto con estadísticas
            stats_text = f'Media: {media:.3f}\nMediana: {mediana:.3f}\nDesv. Est.: {std:.3f}\nN: {n_datos}'
                
            # Posicionar el texto en la esquina superior derecha
            ax.text(0.75, 0.75, stats_text, transform=ax.transAxes, 
                    bbox=dict(boxstyle='round', facecolor='white', alpha=0.8),
                    verticalalignment='top', fontsize=10)
        
        # Configurar cada subplot
        ax.set_title(title_band, fontsize=14, pad=10)
        ax.set_xlabel('periodogram peak frequency', fontsize=12)
        ax.set_ylabel('Number of Sources', fontsize=12)
        ax.grid(True, alpha=0.3)
    
    # Título global de la figura
    fig.suptitle(f'Period Distribution Analysis - {folder_type}', 
                fontsize=18, fontweight='bold', y=0.98)
    
    # Ajustar el layout
    plt.tight_layout()
    plt.subplots_adjust(top=0.93)  # Dejar espacio para el título global
    
    # Guardar la figura
    filename = f'histogram_{folder_type}.png'
    filepath = os.path.join(directory_results, filename)
    plt.savefig(filepath, dpi=300, bbox_inches='tight')
    plt.close()
    
    print(f"Histogram saved in: {filepath}")
    
if __name__ == "__main__":
    directory = "dataset"
    results_dir = "results"
    directory_results = os.path.join(directory,results_dir)
    for folder_type in ["rrlyrae"]:
        # directory of the type
        d_folder_type = os.path.join(directory, folder_type)
        # read the frequencies
        df = pd.read_csv(f'dataset/frequencies_data_{folder_type}.csv')
        # plot the histogram
        plot_histogram(df, folder_type)
        