"""
generate_indices.py

Autor: alex_strange
Fecha: 22 de noviembre de 2024

Descripción:
Este script procesa imágenes satelitales de Sentinel y Landsat para calcular índices de 
vegetación (NDVI y EVI) y los guarda en archivos GeoTIFF con dos bandas. Las imágenes se 
organizan por temporada (initial, refresh, finalize) y por fuente (Sentinel, Landsat).

Propósito:
- Automatizar el cálculo de índices NDVI y EVI para análisis de vegetación.
- Procesar bandas espectrales de Sentinel (B8, B4, B2) y Landsat (SR_B5, SR_B4, SR_B2).
- Generar imágenes GeoTIFF con índices organizados por polígono y temporada.

Entradas:
- Directorios con imágenes satelitales (`sentinel_img` y `landsat_img`) organizados por temporadas.

Salidas:
- Archivos GeoTIFF con índices NDVI (banda 1) y EVI (banda 2) en `indices/`.

Dependencias:
- rasterio
- numpy

"""

import os
import rasterio
import numpy as np

# Directorios de entrada y salida
sentinel_dir = "sentinel_img"
landsat_dir = "landsat_img"
output_dir = "indices"
seasons = {
    "initial": ("2024-05-01", "2024-06-30"),
    "refresh": ("2024-07-01", "2024-07-31"),
    "finalize": ("2024-08-01", "2024-09-30"),
}

# Crear carpetas de salida para cada temporada
for season in seasons.keys():
    os.makedirs(os.path.join(output_dir, f"sentinel/{season}"), exist_ok=True)
    os.makedirs(os.path.join(output_dir, f"landsat/{season}"), exist_ok=True)

# Función para calcular NDVI
def calculate_ndvi(nir, red):
    with np.errstate(divide="ignore", invalid="ignore"):
        ndvi = (nir - red) / (nir + red + 1e-10)
    return np.nan_to_num(ndvi, nan=0.0, posinf=0.0, neginf=0.0)

# Función para calcular EVI
def calculate_evi(nir, red, blue):
    with np.errstate(divide="ignore", invalid="ignore"):
        evi = 2.5 * (nir - red) / (nir + 6 * red - 7.5 * blue + 1)
    return np.nan_to_num(evi, nan=0.0, posinf=0.0, neginf=0.0)

# Función para calcular índices y guardar en TIFF
def calculate_indices_from_bands(nir_path, red_path, blue_path, output_path):
    try:
        with rasterio.open(nir_path) as nir_src, \
             rasterio.open(red_path) as red_src, \
             rasterio.open(blue_path) as blue_src:

            nir = nir_src.read(1).astype(np.float32)
            red = red_src.read(1).astype(np.float32)
            blue = blue_src.read(1).astype(np.float32)

            ndvi = calculate_ndvi(nir, red)
            evi = calculate_evi(nir, red, blue)

            meta = nir_src.meta.copy()
            meta.update({"count": 2, "dtype": "float32"})

            with rasterio.open(output_path, "w", **meta) as dst:
                dst.write(ndvi, 1)
                dst.write(evi, 2)

            print(f"Índices guardados en: {output_path}")
    except Exception as e:
        print(f"Error al calcular índices: {e}")

# Procesar Sentinel
for season in seasons.keys():
    season_dir = os.path.join(sentinel_dir, season)
    output_season_dir = os.path.join(output_dir, f"sentinel/{season}")
    for polygon_id in range(1, 10):  # Polígonos del 1 al 9
        bands = {
            "red": f"{season_dir}/Polygon_{polygon_id}_B4.B4.tif",
            "nir": f"{season_dir}/Polygon_{polygon_id}_B8.B8.tif",
            "blue": f"{season_dir}/Polygon_{polygon_id}_B2.B2.tif",
        }
        if all(os.path.exists(band_path) for band_path in bands.values()):
            output_path = os.path.join(output_season_dir, f"Polygon_{polygon_id}_indices.tif")
            calculate_indices_from_bands(bands["nir"], bands["red"], bands["blue"], output_path)

# Procesar Landsat
for season in seasons.keys():
    season_dir = os.path.join(landsat_dir, season)
    output_season_dir = os.path.join(output_dir, f"landsat/{season}")
    for file_name in os.listdir(season_dir):
        if file_name.endswith(".tif"):
            input_path = os.path.join(season_dir, file_name)
            output_path = os.path.join(output_season_dir, file_name.replace(".tif", "_indices.tif"))
            try:
                with rasterio.open(input_path) as src:
                    nir = src.read(5).astype(np.float32)  # Banda NIR
                    red = src.read(4).astype(np.float32)  # Banda Red
                    blue = src.read(2).astype(np.float32)  # Banda Blue

                    ndvi = calculate_ndvi(nir, red)
                    evi = calculate_evi(nir, red, blue)

                    meta = src.meta.copy()
                    meta.update({"count": 2, "dtype": "float32"})

                    with rasterio.open(output_path, "w", **meta) as dst:
                        dst.write(ndvi, 1)
                        dst.write(evi, 2)

                    print(f"Índices guardados en: {output_path}")
            except Exception as e:
                print(f"Error al calcular índices para {file_name}: {e}")

