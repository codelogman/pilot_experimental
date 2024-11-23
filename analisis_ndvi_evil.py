"""
analisis_ndvi_evil.py

Autor: alex_strange
Fecha: 22 de noviembre de 2024

Descripción:
Este script analiza imágenes de índices NDVI y EVI generadas a partir de Landsat y Sentinel, 
organizadas por temporada (initial, refresh, finalize). Calcula estadísticas básicas (mínimo, 
máximo, media, desviación estándar) para cada índice y exporta los resultados en formato HTML.

Propósito:
- Procesar imágenes de índices NDVI y EVI generadas previamente.
- Calcular estadísticas básicas para evaluar la calidad de los índices.
- Generar un informe HTML que detalle las estadísticas por archivo y temporada.

Entradas:
- Directorios de índices NDVI/EVI (`indices/landsat` y `indices/sentinel`) organizados por temporadas.

Salidas:
- Archivo HTML (`ndvi_evi_analysis.html`) con estadísticas por índice, temporada y dataset.

Dependencias:
- rasterio
- numpy
- pandas

"""

import os
import rasterio
import numpy as np
import pandas as pd
import warnings

# Ignorar warnings generales
warnings.filterwarnings("ignore", category=UserWarning, module="rasterio")

# Directorios de entrada
landsat_indices_dir = "indices/landsat"
sentinel_indices_dir = "indices/sentinel"
output_html = "ndvi_evi_analysis.html"

# Tabla para almacenar los resultados
results_table = []

# Función para calcular estadísticas
def calculate_statistics(data):
    return {
        "Min": np.min(data),
        "Max": np.max(data),
        "Mean": np.mean(data),
        "StdDev": np.std(data),
    }

# Procesar archivos de índices de Sentinel y Landsat
for dir_path, dataset_name in [
    (landsat_indices_dir, "Landsat"),
    (sentinel_indices_dir, "Sentinel"),
]:
    for season in os.listdir(dir_path):  # Procesar por temporada
        season_path = os.path.join(dir_path, season)
        if not os.path.isdir(season_path):
            continue
        
        for file_name in os.listdir(season_path):
            if file_name.endswith(".tif"):
                file_path = os.path.join(season_path, file_name)
                print(f"Procesando archivo: {file_path}")

                try:
                    with rasterio.open(file_path) as src:
                        if src.count < 2:
                            print(f"Advertencia: {file_name} no tiene suficientes bandas para NDVI y EVI.")
                            continue

                        ndvi = src.read(1).astype(np.float32)
                        evi = src.read(2).astype(np.float32)

                        # Calcular estadísticas
                        ndvi_stats = calculate_statistics(ndvi)
                        evi_stats = calculate_statistics(evi)

                        # Agregar resultados a la tabla
                        results_table.append({
                            "File": file_name,
                            "Season": season,
                            "Source": dataset_name,
                            "NDVI Min": ndvi_stats["Min"],
                            "NDVI Max": ndvi_stats["Max"],
                            "NDVI Mean": ndvi_stats["Mean"],
                            "NDVI StdDev": ndvi_stats["StdDev"],
                            "EVI Min": evi_stats["Min"],
                            "EVI Max": evi_stats["Max"],
                            "EVI Mean": evi_stats["Mean"],
                            "EVI StdDev": evi_stats["StdDev"],
                        })

                except Exception as e:
                    print(f"Error procesando {file_path}: {e}")

# Crear un DataFrame y exportar a HTML
df = pd.DataFrame(results_table)
df.to_html(output_html, index=False, float_format="{:.2f}".format)

print(f"Análisis completado. Resultados guardados en {output_html}")

