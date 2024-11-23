"""
analisis_completo.py

Autor: alex_strange
Fecha: 22 de noviembre de 2024

Descripción:
Este script analiza imágenes geoespaciales descargadas de Landsat y Sentinel para 
diferentes etapas estacionales (initial, refresh, finalize). Calcula estadísticas 
básicas como el mínimo, máximo, media, y desviación estándar para cada banda de las 
imágenes GeoTIFF y genera un informe en formato HTML.

Propósito:
- Procesar imágenes Landsat y Sentinel para obtener estadísticas básicas.
- Organizar estadísticas por etapa estacional (initial, refresh, finalize).
- Generar un informe visual en HTML para facilitar la inspección de los datos.

Entradas:
- Directorios base (`landsat_img` y `sentinel_img`) con imágenes en formato GeoTIFF.
- Subcarpetas organizadas por etapas estacionales.

Salidas:
- Un archivo HTML (`analysis_statistics.html`) con las estadísticas por etapa y dataset.

Dependencias:
- rasterio
- numpy
- jinja2

"""

import os
import rasterio
from jinja2 import Template
import numpy as np
import warnings

# Suprimir los warnings de Rasterio
warnings.filterwarnings("ignore", category=rasterio.errors.NotGeoreferencedWarning)
warnings.filterwarnings("ignore", message="TIFFReadDirectory:Sum of Photometric type-related color channels and ExtraSamples doesn't match SamplesPerPixel")

# Directorios base de entrada y salida
base_landsat_dir = "landsat_img"
base_sentinel_dir = "sentinel_img"
output_html = "analysis_statistics.html"

# Plantilla HTML
html_template = """
<!DOCTYPE html>
<html>
<head>
    <title>Análisis de Imágenes por Temporada</title>
    <style>
        table {
            border-collapse: collapse;
            width: 100%;
        }
        th, td {
            text-align: left;
            padding: 8px;
            border: 1px solid #ddd;
        }
        th {
            background-color: #f4f4f4;
        }
    </style>
</head>
<body>
    <h1>Estadísticas de Imágenes Geoespaciales</h1>
    {% for stage, datasets in seasonal_data.items() %}
    <h2>Temporada: {{ stage }}</h2>
    {% for dataset_name, stats in datasets.items() %}
    <h3>{{ dataset_name }}</h3>
    <table>
        <thead>
            <tr>
                <th>Archivo</th>
                <th>Banda</th>
                <th>Mínimo</th>
                <th>Máximo</th>
                <th>Media</th>
                <th>Desviación Estándar</th>
            </tr>
        </thead>
        <tbody>
            {% for stat in stats %}
            <tr>
                <td>{{ stat.file }}</td>
                <td>{{ stat.band }}</td>
                <td>{{ stat.min }}</td>
                <td>{{ stat.max }}</td>
                <td>{{ stat.mean }}</td>
                <td>{{ stat.std }}</td>
            </tr>
            {% endfor %}
        </tbody>
    </table>
    {% endfor %}
    {% endfor %}
</body>
</html>
"""

# Función para calcular estadísticas
def calculate_statistics(data, nodata_value):
    if nodata_value is not None:
        data = data[data != nodata_value]  # Filtrar nodata
    if data.size == 0:
        return {"Min": None, "Max": None, "Mean": None, "Std": None}
    return {
        "Min": float(data.min()),
        "Max": float(data.max()),
        "Mean": float(data.mean()),
        "Std": float(data.std()),
    }

# Función para analizar un archivo .tif
def analyze_tif(file_path, dataset_name):
    stats = []
    try:
        with rasterio.open(file_path) as src:
            nodata_value = src.nodata  # Obtener valor nodata
            for band in range(1, src.count + 1):
                data = src.read(band)
                band_stats = calculate_statistics(data, nodata_value)
                stats.append({
                    "file": os.path.basename(file_path),
                    "band": band,
                    "min": band_stats["Min"],
                    "max": band_stats["Max"],
                    "mean": band_stats["Mean"],
                    "std": band_stats["Std"],
                })
    except Exception as e:
        print(f"Error procesando {file_path} en {dataset_name}: {e}")
    return stats

# Recopilar estadísticas por temporada
seasonal_data = {}
for stage in ["initial", "refresh", "finalize"]:
    seasonal_data[stage] = {"Landsat": [], "Sentinel": []}
    for base_dir, dataset_name in [(base_landsat_dir, "Landsat"), (base_sentinel_dir, "Sentinel")]:
        stage_dir = os.path.join(base_dir, stage)
        if not os.path.exists(stage_dir):
            continue
        for filename in os.listdir(stage_dir):
            if filename.endswith(".tif"):
                file_path = os.path.join(stage_dir, filename)
                seasonal_data[stage][dataset_name].extend(analyze_tif(file_path, dataset_name))

# Generar el archivo HTML
template = Template(html_template)
html_content = template.render(seasonal_data=seasonal_data)

with open(output_html, "w") as f:
    f.write(html_content)

print(f"Estadísticas guardadas en {output_html}. Ábrelo en tu navegador para inspeccionar.")

