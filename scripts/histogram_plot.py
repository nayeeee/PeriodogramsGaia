import os
import pickle
import numpy as np
import matplotlib.pyplot as plt
import sys
from tqdm import tqdm
sys.path.append('..')


def plot_histogram(data_dict, folder_type,
                      bins=30, alpha=0.7, figsize=(16, 12),
                      mostrar_estadisticas=True, mostrar_curva_normal=False):
    """
    Función para crear 4 histogramas (2x2) desde un diccionario de bandas
    
    Parámetros:
    -----------
    data_dict : dict
        Diccionario con la estructura:
        {'g': [(real_period, candidate_period), ...],
         'bp': [(real_period, candidate_period), ...],
         'rp': [(real_period, candidate_period), ...],
         'multiband': [(real_period, candidate_period), ...]}
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
    results_dir = "results"
    
    # Crear la figura con 4 subplots en disposición 2x2
    fig, axes = plt.subplots(2, 2, figsize=figsize)
    axes = axes.flatten()  # Aplanar para facilitar la iteración
    
    # Crear cada histograma
    for i, (banda, color, titulo_banda) in enumerate(zip(bandas, colores, titulos_bandas)):
        ax = axes[i]
        
        # Verificar si la banda existe en el diccionario y tiene datos
        if banda in data_dict and len(data_dict[banda]) > 0:
            # Extraer candidate_period (posición 1) de las tuplas
            datos = np.array([tupla[1] for tupla in data_dict[banda]])
            
            # Crear el histograma
            n, bins_edges, patches = ax.hist(datos, bins=bins, alpha=alpha, 
                                           color=color, edgecolor='black', 
                                           density=mostrar_curva_normal)
            
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
        else:
            # Si no hay datos para esta banda, mostrar mensaje
            ax.text(0.5, 0.5, 'No data available', 
                   transform=ax.transAxes, ha='center', va='center',
                   fontsize=14, style='italic', color='gray')
        
        # Configurar cada subplot
        ax.set_title(titulo_banda, fontsize=14, pad=10)
        ax.set_xlabel('Period', fontsize=12)
        ax.set_ylabel('Number of Sources', fontsize=12)
        ax.grid(True, alpha=0.3)
    
    # Título global de la figura
    fig.suptitle(f'Period Distribution Analysis - {type_lc}', 
                fontsize=18, fontweight='bold', y=0.98)
    
    # Ajustar el layout
    plt.tight_layout()
    plt.subplots_adjust(top=0.93)  # Dejar espacio para el título global
    
    # Guardar la figura
    filename = f'histogram_{folder_type}_{band}.png'
    filepath = os.path.join(results_dir, filename)
    plt.savefig(filepath, dpi=300, bbox_inches='tight')
    plt.close()
    
    print(f"Histogram saved in: {filepath}")
    
if __name__ == "__main__":
    directory = "dataset"
    results_dir = "results"
    for folder_type in ["rrlyrae"]:
        # directory of the type
        d_folder_type = os.path.join(directory, folder_type)
        # list of the periods 
        # {'g': [(real_period, candidate_period), ...], 
        # 'bp': [(real_period, candidate_period), ...], 
        # 'rp': [(real_period, candidate_period), ...], 
        # 'multiband': [(real_period, candidate_period), ...]}
        # read the periods
        with open(os.path.join(results_dir, f'periods_{folder_type}.pkl'), 'rb') as f:
            dict_periods = pickle.load(f)
        # plot the histogram
        plot_histogram(dict_periods, folder_type)
        