"""
visual_inspection_mask.py

Autor: alex_strange

Descripción:
Este script genera un mapa interactivo en HTML que visualiza máscaras geoespaciales 
provenientes de imágenes satelitales (Landsat y Sentinel). Utiliza el archivo KML de 
referencia para superponer las máscaras en el mapa, organizadas por temporada 
(initial, refresh, finalize).

Propósito:
- Inspeccionar visualmente las máscaras generadas (bordes de áreas agrícolas).
- Superponer las máscaras como capas en un mapa basado en Folium.
- Permitir la comparación entre las máscaras de Landsat y Sentinel en distintas temporadas.

Entradas:
- Archivo KML con polígonos de referencia.
- Directorios con máscaras de Landsat (`masks/landsat`) y Sentinel (`masks/sentinel`).

Salidas:
- Archivo HTML (`mask_visualization_map.html`) con el mapa interactivo.

Dependencias:
- geopandas
- rasterio
- numpy
- folium
"""

import folium
import geopandas as gpd
import rasterio
import numpy as np
import os

# Archivos de entrada
kml_file = "test site.kml"
landsat_base_dir = "indices/landsat"  # Carpeta base con índices Landsat
sentinel_base_dir = "indices/sentinel"  # Carpeta base con índices Sentinel
seasons = ["initial", "refresh", "finalize"]  # Temporadas

# Leer archivo KML
geo_data = gpd.read_file(kml_file)

# Reproyectar si es necesario
if geo_data.crs != "EPSG:4326":
    geo_data = geo_data.to_crs(epsg=4326)

# Obtener los límites
bounds = geo_data.total_bounds  # [minx, miny, maxx, maxy]

# Crear el mapa centrado y ajustado a los límites
m = folium.Map(location=[(bounds[1] + bounds[3]) / 2, (bounds[0] + bounds[2]) / 2], zoom_start=12)
m.fit_bounds([[bounds[1], bounds[0]], [bounds[3], bounds[2]]])

# Agregar las geometrías del KML al mapa
folium.GeoJson(
    geo_data,
    name="KML Polygons",
    style_function=lambda x: {"color": "blue", "weight": 2, "fillOpacity": 0.2},
).add_to(m)

# Función para superponer imágenes en el mapa
def overlay_tiff_images(season_dir, color, name_prefix, map_obj):
    for tiff_file in os.listdir(season_dir):
        if tiff_file.endswith(".tif"):
            tiff_path = os.path.join(season_dir, tiff_file)
            with rasterio.open(tiff_path) as src:
                bounds = src.bounds
                ndvi_band = src.read(1)  # Leer la banda NDVI
                ndvi_normalized = (ndvi_band - ndvi_band.min()) / (ndvi_band.max() - ndvi_band.min() + 1e-10)  # Normalizar valores

                # Crear una matriz RGBA basada en el color
                overlay = np.zeros((ndvi_normalized.shape[0], ndvi_normalized.shape[1], 4), dtype=np.float32)
                overlay[..., 0] = color[0] * ndvi_normalized  # Componente roja
                overlay[..., 1] = color[1] * ndvi_normalized  # Componente verde
                overlay[..., 2] = color[2] * ndvi_normalized  # Componente azul
                overlay[..., 3] = ndvi_normalized  # Opacidad basada en NDVI

            # Agregar al mapa como capa de imagen
            folium.raster_layers.ImageOverlay(
                image=overlay,
                bounds=[[bounds.bottom, bounds.left], [bounds.top, bounds.right]],
                name=f"{name_prefix} ({os.path.basename(season_dir)}) {tiff_file}",
                opacity=0.6,
                interactive=True,
                cross_origin=False,
            ).add_to(map_obj)

# Superponer imágenes por cada temporada
for season in seasons:
    landsat_dir = os.path.join(landsat_base_dir, season)
    sentinel_dir = os.path.join(sentinel_base_dir, season)

    if os.path.exists(landsat_dir):
        overlay_tiff_images(landsat_dir, (1, 0, 0), f"Landsat NDVI - {season.capitalize()}", m)
    if os.path.exists(sentinel_dir):
        overlay_tiff_images(sentinel_dir, (0, 1, 0), f"Sentinel NDVI - {season.capitalize()}", m)

# Agregar controles de capas
folium.LayerControl().add_to(m)

# Guardar el mapa en un archivo HTML
map_output = "ndvi_evi_visualization_map.html"
m.save(map_output)
print(f"Mapa guardado en {map_output}. Ábrelo en un navegador para inspeccionar.")

