"""
sentinnel_download_script.py

Descripción:
Este script automatiza la descarga de imágenes satelitales de Sentinel-2 desde una fuente específica (por ejemplo, API de Copernicus). 
Las imágenes descargadas pueden ser usadas para análisis de teledetección, monitoreo ambiental, o procesamiento adicional como segmentación.

Estructura de Entrada:
- Parámetros del área de interés (AOI) en formato GeoJSON, KML o coordenadas.
- Fechas de inicio y fin para la consulta de imágenes.
- Parámetros opcionales como nivel de nube permitido, bandas específicas, y resolución deseada.

Estructura de Salida:
- Archivos descargados en formato SAFE o TIFF, organizados por fecha y AOI.
- Metadatos relacionados con cada imagen, almacenados en un archivo separado.

Componentes principales:
1. Interacción con la API de descarga de Sentinel.
2. Validación y filtrado de imágenes según criterios definidos por el usuario.
3. Organización y almacenamiento de las imágenes descargadas.
4. Registro de errores y resumen de la descarga.

Dependencias:
- Python >= 3.8
- Requests
- Shapely
- Geopandas
- SentinelHub-py (u otra librería específica para la API)

alex_strange
"""


import ee
import os
import geemap

# Inicializar Earth Engine
ee.Authenticate()
ee.Initialize()

# Archivo KML
kml_file = "test site.kml"

# Directorio base de salida
base_output_dir = "sentinel_img"
os.makedirs(base_output_dir, exist_ok=True)

# Función para parsear el KML y extraer coordenadas
def parse_kml(file_path):
    import xml.etree.ElementTree as ET
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

# Función para descargar una banda específica
def download_band(polygon, band_name, index, start_date, end_date, output_dir):
    try:
        aoi = ee.Geometry.Polygon([polygon])
        collection = (
            ee.ImageCollection("COPERNICUS/S2_SR_HARMONIZED")
            .filterBounds(aoi)
            .filterDate(start_date, end_date)
            .filterMetadata("CLOUDY_PIXEL_PERCENTAGE", "less_than", 30)
            .select([band_name])
        )

        # Verificar si hay imágenes en la colección
        if collection.size().getInfo() == 0:
            print(f"No se encontraron imágenes para la banda {band_name} en el Polígono {index}.")
            return None

        # Obtener la mediana y recortar
        image = collection.median().clip(aoi)

        # Definir la ruta de salida (sin duplicar el nombre de la banda)
        output_path = os.path.join(output_dir, f"Polygon_{index}_{band_name}.tif")

        # Descargar la banda
        geemap.ee_export_image(
            ee_object=image,
            filename=output_path,
            scale=10,  # Mantener la resolución de Sentinel-2
            region=aoi.getInfo()["coordinates"],
            file_per_band=True,
        )
        print(f"Banda {band_name} guardada: {output_path}")
        return output_path

    except Exception as e:
        print(f"Error procesando la banda {band_name} del Polígono {index}: {str(e)}")
        return None

# Descargar las bandas clave para cada polígono y etapa
def download_sentinel_bands(polygons, start_date, end_date, stage_dir):
    for i, polygon in enumerate(polygons, start=1):
        print(f"\nProcesando Polígono {i} de {len(polygons)} para la etapa {stage_dir}...")
        for band in ["B8", "B4", "B3", "B2"]:  # NIR, Red, Green, Blue
            download_band(polygon, band, i, start_date, end_date, stage_dir)

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
    download_sentinel_bands(polygons, start_date, end_date, stage_dir)

