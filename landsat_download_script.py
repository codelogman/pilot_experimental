"""
landsat_download_script.py

Autor: alex_strange
Fecha: 22 de noviembre de 2024

Descripción:
Este script descarga imágenes satelitales Landsat 8 para diferentes etapas estacionales 
(initial, refresh, finalize) de áreas agrícolas definidas en un archivo KML. Las imágenes 
se procesan para calcular índices NDVI y EVI, se exportan como archivos GeoTIFF y se 
analizan para garantizar la calidad de los datos.

Propósito:
- Automatizar la descarga y procesamiento de imágenes Landsat 8 desde Google Earth Engine.
- Calcular índices de vegetación (NDVI y EVI) para análisis agrícola.
- Generar imágenes organizadas por etapa estacional para validación y modelado posterior.

Entradas:
- Archivo KML que define los polígonos de las áreas agrícolas.
- Rango de fechas para cada etapa estacional.

Salidas:
- Imágenes GeoTIFF procesadas con índices NDVI y EVI.
- Análisis estadístico de las imágenes descargadas.

Dependencias:
- geemap
- rasterio
- numpy
- earthengine-api

Notas:
- Requiere autenticación con Google Earth Engine.
- Configura las rutas adecuadas para el archivo KML y los directorios de salida antes de ejecutar.

Última modificación:
22 de noviembre de 2024
"""


import ee
import os
import xml.etree.ElementTree as ET
import geemap
import rasterio
import numpy as np

# Inicializar Earth Engine
ee.Authenticate()
ee.Initialize()

# Archivo KML
kml_file = "test site.kml"

# Directorio base de salida
base_output_dir = "landsat_img"
os.makedirs(base_output_dir, exist_ok=True)

# Función para parsear el KML y extraer coordenadas
def parse_kml(file_path):
    tree = ET.parse(file_path)
    root = tree.getroot()
    namespace = {"kml": "http://www.opengis.net/kml/2.2"}
    polygons = []

    for placemark in root.findall(".//kml:Placemark", namespace):
        coordinates = placemark.find(".//kml:coordinates", namespace)
        if coordinates is None or not coordinates.text.strip():
            continue
        coords_list = [
            [float(coord.split(",")[0]), float(coord.split(",")[1])]
            for coord in coordinates.text.strip().split()
        ]
        polygons.append(coords_list)

    return polygons

# Función para calcular NDVI
def calculate_ndvi(image):
    nir = image.select("SR_B5")
    red = image.select("SR_B4")
    ndvi = nir.subtract(red).divide(nir.add(red)).rename("NDVI")
    return image.addBands(ndvi)

# Función para calcular EVI
def calculate_evi(image):
    nir = image.select("SR_B5")
    red = image.select("SR_B4")
    blue = image.select("SR_B2")
    evi = (
        nir.subtract(red)
        .multiply(2.5)
        .divide(nir.add(red.multiply(6)).subtract(blue.multiply(7.5)).add(1))
        .rename("EVI")
    )
    return image.addBands(evi)

# Función para analizar y validar las imágenes descargadas
def analyze_image(file_path):
    try:
        with rasterio.open(file_path) as src:
            print(f"\nAnalizando archivo: {file_path}")
            print(f"Bands: {src.count}")
            print(f"Width, Height: {src.width}, {src.height}")
            print(f"CRS: {src.crs}")
            print(f"Bounds: {src.bounds}")
            print(f"Data Type: {src.dtypes}")

            for i in range(1, src.count + 1):
                band = src.read(i)
                print(f"  Banda {i}:")
                print(f"    Min: {np.min(band):.2f}")
                print(f"    Max: {np.max(band):.2f}")
                print(f"    Media: {np.mean(band):.2f}")
                print(f"    Desviación Estándar: {np.std(band):.2f}")
    except Exception as e:
        print(f"Error al analizar {file_path}: {str(e)}")

# Función para descargar imágenes de Landsat
def download_landsat_images(polygons, start_date, end_date, stage_dir):
    for i, polygon in enumerate(polygons, start=1):
        print(f"\nProcesando Polígono {i} de {len(polygons)} para la etapa {stage_dir}...")
        try:
            aoi = ee.Geometry.Polygon([polygon])
            collection = (
                ee.ImageCollection("LANDSAT/LC08/C02/T1_L2")
                .filterBounds(aoi)
                .filterDate(start_date, end_date)
                .filterMetadata("CLOUD_COVER", "less_than", 30)
            )
            
            # Verificar si hay imágenes en la colección
            if collection.size().getInfo() == 0:
                print(f"No se encontraron imágenes para el Polígono {i} en la etapa {stage_dir}.")
                continue

            # Calcular NDVI y EVI
            image = collection.median().clip(aoi)
            image = calculate_ndvi(image)
            image = calculate_evi(image)

            # Definir la ruta de salida
            output_path = os.path.join(stage_dir, f"Polygon_{i}_landsat8.tif")

            # Descargar la imagen
            geemap.ee_export_image(
                ee_object=image,
                filename=output_path,
                scale=30,
                region=aoi.getInfo()["coordinates"],
                file_per_band=False,
            )
            print(f"Imagen guardada: {output_path}")

            # Analizar la imagen descargada
            analyze_image(output_path)

        except Exception as e:
            print(f"Error procesando el Polígono {i}: {str(e)}")

# Etapas estacionales y rangos de fechas
seasonal_stages = {
    "initial": ("2024-05-01", "2024-06-30"),
    "refresh": ("2024-07-01", "2024-07-31"),
    "finalize": ("2024-08-01", "2024-09-30"),
}

# Parsear el archivo KML
polygons = parse_kml(kml_file)

# Ejecutar la descarga por etapa
for stage, (start_date, end_date) in seasonal_stages.items():
    stage_dir = os.path.join(base_output_dir, stage)
    os.makedirs(stage_dir, exist_ok=True)
    download_landsat_images(polygons, start_date, end_date, stage_dir)

