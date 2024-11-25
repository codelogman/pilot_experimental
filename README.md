# Agricultural Field Border Detection

## Descripción

Este repositorio contiene todos los scripts, datos y notebooks necesarios para detectar y analizar automáticamente bordes agrícolas mediante imágenes satelitales (Landsat y Sentinel). Se emplean índices de vegetación como NDVI y EVI, junto con algoritmos de detección de bordes.

---

## Estructura del Proyecto

```plaintext

pilot_experimental/
├── analysis_statistics.html       # Análisis estadístico y métricas de los datos procesados.
├── api_prototype.py               # Implementación prototipo de una API para integrar servicios de detección de bordes agrícolas.
├── dataset/                       # Directorio que contiene datasets para el fine-tuning de SAM.
│   ├── train_annotations.json     # Anotaciones del dataset de entrenamiento en formato COCO.
│   ├── train_images/              # Carpeta con imágenes del dataset de entrenamiento.
│   ├── val_annotations.json       # Anotaciones del dataset de validación en formato COCO.
│   └── val_images/                # Carpeta con imágenes del dataset de validación.
├── diagrama.png                   # Diagrama que ilustra el flujo de trabajo completo, incluyendo la API y la integración del fine-tuning.
├── Dockerfile                     # Dockerfile para contenerizar el flujo de trabajo y sus dependencias.
├── final_check_integrity.py       # Script para garantizar la integridad final de los archivos generados y sus salidas.
├── fine_tuning_sam.py             # Script para realizar el fine-tuning del modelo SAM utilizando datasets personalizados.
├── generate_sobel_sentinel.py     # Script para procesar imágenes de Sentinel utilizando detección de bordes con Sobel.
├── Jenkinsfile                    # Archivo Jenkinsfile para automatizar el despliegue y las pruebas del pipeline.
├── k8s-deployment.yaml            # Configuración de despliegue para Kubernetes, asegurando escalabilidad.
├── ndvi_evi_analysis.html         # Análisis detallado de NDVI y EVI generado a partir de imágenes de Sentinel.
├── ndvi_evi_visualization_map.html # Mapa interactivo para visualizar valores de NDVI y EVI en los polígonos definidos.
├── puppet-manifest.pp             # Archivo de configuración Puppet para la gestión de infraestructura.
├── sam_2_apply_colored2.py        # Script para aplicar la segmentación de SAM, generar máscaras RGBA y exportar a GPKG/GeoJSON.
├── sentinnel_download_script.py   # Script para descargar imágenes satelitales Sentinel-2 basándose en áreas poligonales definidas en un archivo KML.
├── tech_specs.txt                 # Documentación técnica que detalla el flujo de trabajo, metodologías y cumplimiento con los requisitos del RFP.
├── test site.kml                  # Archivo KML de entrada que define las áreas poligonales de interés para la detección de bordes agrícolas.
├── unet_model.h5                  # Archivo de modelo UNet reservado para futuras integraciones.
└── verificar_simetria.py          # Script para verificar la alineación espacial y consistencia entre las imágenes originales y las máscaras generadas.
