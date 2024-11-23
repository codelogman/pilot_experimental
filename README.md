# Agricultural Field Border Detection

## Descripción

Este repositorio contiene todos los scripts, datos y notebooks necesarios para detectar y analizar automáticamente bordes agrícolas mediante imágenes satelitales (Landsat y Sentinel). Se emplean índices de vegetación como NDVI y EVI, junto con algoritmos de detección de bordes.

---

## Estructura del Proyecto

```plaintext
pilot/
├── analisis_completo.py              # Análisis general de las imágenes procesadas
├── analisis_ndvi_evil.py             # Cálculo y análisis de estadísticas de NDVI y EVI
├── extract_polygons.py               # Extracción de polígonos a partir de datos geoespaciales
├── generate_indices.py               # Cálculo de índices NDVI y EVI
├── generate_mask_sobel.py            # Generación de máscaras usando el algoritmo Sobel
├── jupyter_notebook/
│   └── dataset_construction.ipynb    # Notebook para la construcción de datasets
├── landsat_download_script.py        # Descarga de imágenes Landsat
├── landsat_img/                      # Imágenes Landsat organizadas por temporada
│   ├── finalize/
│   ├── initial/
│   └── refresh/
├── polygons.json                     # Polígonos geoespaciales en formato JSON
├── sentinel_img/                     # Imágenes Sentinel organizadas por temporada
│   ├── finalize/
│   ├── initial/
│   └── refresh/
├── sentinnel_download_script.py      # Descarga de imágenes Sentinel
├── test site.kml                     # Archivo KML con datos de referencia
├── test_polygons.py                  # Script de prueba para validar geometrías
├── visual_inspection_mask.py         # Visualización de máscaras en un mapa interactivo
└── visual_inspection_ndvi_evil.py    # Visualización de NDVI/EVI en un mapa interactivo
