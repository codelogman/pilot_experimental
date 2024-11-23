"""
generate_mask_sobel.py

Autor: alex_strange
Fecha: 22 de noviembre de 2024

Descripción:
Este script genera máscaras de bordes a partir de imágenes de índices NDVI y EVI para 
áreas agrícolas, utilizando el algoritmo Sobel para la detección de bordes. Las máscaras 
se procesan y limpian con operaciones morfológicas y se guardan como archivos GeoTIFF.

Por qué se eligió el algoritmo Sobel:
El algoritmo de detección de bordes Sobel se utiliza debido a su simplicidad y eficiencia 
para identificar cambios graduales en las imágenes, como los límites entre áreas de cultivo 
y otras superficies. Es particularmente adecuado para datos de índices de vegetación, ya que 
realza las transiciones significativas en los valores de NDVI y EVI. Además, combina bien 
con técnicas de preprocesamiento como el suavizado y la normalización, proporcionando 
máscaras de bordes claras y detalladas para análisis geoespacial.

Propósito:
- Detectar bordes en imágenes geoespaciales combinando NDVI y EVI.
- Generar máscaras binarias que resalten los límites de áreas agrícolas.
- Aplicar técnicas de limpieza para mejorar la calidad de las máscaras.

Entradas:
- Directorio de imágenes de índices (`indices`) con bandas NDVI y EVI.

Salidas:
- Directorio de máscaras (`masks`) con archivos GeoTIFF binarios.

Dependencias:
- rasterio
- numpy
- opencv-python
- scikit-image

"""
import os
import cv2
import numpy as np
import rasterio
from skimage import filters

# Directorios de entrada y salida
indices_dir = "indices"
masks_dir = "masks"
seasons = ["initial", "refresh", "finalize"]

# Crear directorios de salida para cada temporada
for dataset in ["landsat", "sentinel"]:
    for season in seasons:
        os.makedirs(os.path.join(masks_dir, dataset, season), exist_ok=True)

# Función para suavizar la imagen
def smooth_image(image, kernel_size=5):
    return cv2.GaussianBlur(image, (kernel_size, kernel_size), 0)

# Función para aplicar operaciones morfológicas
def clean_mask(mask, kernel_size=3):
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (kernel_size, kernel_size))
    cleaned_mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)
    return cleaned_mask

# Función para generar máscara de bordes
def generate_edge_mask(image_path, output_path):
    try:
        with rasterio.open(image_path) as src:
            # Leer las bandas NDVI y EVI
            ndvi_band = src.read(1).astype(np.float32)
            evi_band = src.read(2).astype(np.float32)

            # Normalizar las bandas
            ndvi_norm = (ndvi_band - np.min(ndvi_band)) / (np.max(ndvi_band) - np.min(ndvi_band) + 1e-10)
            evi_norm = (evi_band - np.min(evi_band)) / (np.max(evi_band) - np.min(evi_band) + 1e-10)

            # Fusionar NDVI y EVI en una sola imagen
            combined = (ndvi_norm + evi_norm) / 2.0

            # Suavizar la imagen combinada
            smoothed = smooth_image(combined)

            # Aplicar detección de bordes (Sobel)
            sobel_x = cv2.Sobel(smoothed, cv2.CV_64F, 1, 0, ksize=3)
            sobel_y = cv2.Sobel(smoothed, cv2.CV_64F, 0, 1, ksize=3)
            gradient_magnitude = np.sqrt(sobel_x**2 + sobel_y**2)
            normalized_gradient = (gradient_magnitude / np.max(gradient_magnitude)) * 255

            # Umbralizar para convertir a máscara binaria
            _, binary_mask = cv2.threshold(normalized_gradient.astype(np.uint8), 70, 255, cv2.THRESH_BINARY)

            # Limpiar la máscara con operaciones morfológicas
            cleaned_mask = clean_mask(binary_mask)

            # Guardar la máscara como archivo GeoTIFF
            meta = src.meta.copy()
            meta.update({"count": 1, "dtype": "uint8"})
            with rasterio.open(output_path, "w", **meta) as dst:
                dst.write(cleaned_mask, 1)

            print(f"Mascara generada y guardada en: {output_path}")
    except Exception as e:
        print(f"Error al procesar {image_path}: {e}")

# Procesar archivos para cada temporada y dataset
for dataset in ["landsat", "sentinel"]:
    for season in seasons:
        indices_season_dir = os.path.join(indices_dir, dataset, season)
        masks_season_dir = os.path.join(masks_dir, dataset, season)

        for file_name in os.listdir(indices_season_dir):
            if file_name.endswith(".tif"):
                input_path = os.path.join(indices_season_dir, file_name)
                output_path = os.path.join(masks_season_dir, file_name.replace("_indices", "_mask"))
                generate_edge_mask(input_path, output_path)

print("Generación de máscaras completada. Archivos guardados en los directorios correspondientes.")

