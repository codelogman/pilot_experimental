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
landsat_masks_dir = "masks/landsat"  # Carpeta con máscaras Landsat
sentinel_masks_dir = "masks/sentinel"  # Carpeta con máscaras Sentinel
seasons = ["initial", "refresh", "finalize"]

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

# Función para superponer máscaras en el mapa
def overlay_mask_images(mask_dir, color, name_prefix, season, map_obj):
    season_dir = os.path.join(mask_dir, season)
    for mask_file in os.listdir(season_dir):
        if mask_file.endswith(".tif"):
            mask_path = os.path.join(season_dir, mask_file)
            with rasterio.open(mask_path) as src:
                bounds = src.bounds
                mask_band = src.read(1)  # Leer la máscara
                mask_max = mask_band.max()
                if mask_max > 0:
                    mask_normalized = mask_band / mask_max  # Normalizar valores a rango [0, 1]
                else:
                    mask_normalized = mask_band  # Si el máximo es 0, dejar los valores tal como están
                # Crear una matriz RGBA basada en el color
                overlay = np.zeros((mask_normalized.shape[0], mask_normalized.shape[1], 4), dtype=np.float32)
                overlay[..., 0] = color[0] * mask_normalized  # Componente roja
                overlay[..., 1] = color[1] * mask_normalized  # Componente verde
                overlay[..., 2] = color[2] * mask_normalized  # Componente azul
                overlay[..., 3] = mask_normalized  # Opacidad basada en la máscara

            # Agregar al mapa como capa de imagen
            folium.raster_layers.ImageOverlay(
                image=overlay,
                bounds=[[bounds.bottom, bounds.left], [bounds.top, bounds.right]],
                name=f"{name_prefix} ({season}) {mask_file}",
                opacity=0.6,
                interactive=True,
                cross_origin=False,
            ).add_to(map_obj)

# Procesar y superponer máscaras para cada temporada
for season in seasons:
    overlay_mask_images(landsat_masks_dir, (1, 0, 0), "Landsat Mask", season, m)  # Rojo para Landsat
    overlay_mask_images(sentinel_masks_dir, (0, 1, 0), "Sentinel Mask", season, m)  # Verde para Sentinel

# Agregar controles de capas
folium.LayerControl().add_to(m)

# Guardar el mapa en un archivo HTML
map_output = "mask_visualization_map.html"
m.save(map_output)
print(f"Mapa guardado en {map_output}. Ábrelo en un navegador para inspeccionar.")

