import os
import pickle
import pandas as pd
import sys
sys.path.append("..")
from tqdm import tqdm


for type_lc in ["eclipsing_binary"]:  # Tupla con un elemento
    # Lista de directorios en dataset/{type_lc}
    directories = os.listdir(f"dataset/{type_lc}")
    data_list = []
    for id_matrix in tqdm(directories, desc="Processing"):
        directory = f"dataset/{type_lc}/{id_matrix}/error_matrixes_{id_matrix}.pkl"
        
        with open(directory, 'rb') as f:
            dict_matrix = pickle.load(f)
            
        real_period = dict_matrix['real_period']
        real_frequency = 1 / real_period
            
        # Diccionario para almacenar los datos de esta fila
        row_data = {
            'id': id_matrix,
            'real_frequency': real_frequency
        }
            
        # Extraer las mejores frecuencias para cada banda
        for band in ["g", "bp", "rp", "multiband"]:
            best_frequency = dict_matrix[band][0][0][0]
            row_data[f'best_frequency_{band}'] = best_frequency
            
        data_list.append(row_data)

    # Crear el DataFrame
    df = pd.DataFrame(data_list)
    print("antes de ordenar", df.head())

    # Reordenar las columnas según lo solicitado
    column_order = ['id', 'real_frequency', 'best_frequency_g', 'best_frequency_bp', 'best_frequency_rp', 'best_frequency_multiband']
    df = df[column_order]


    print(f"DataFrame creado con {len(df)} filas")
    print("\nPrimeras 5 filas:")
    print(df.head())

    print("\nInformación del DataFrame:")
    print(df.info())

    df.to_csv(f'dataset/frequencies_data_{type_lc}.csv', index=False)
