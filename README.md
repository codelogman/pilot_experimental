# Pilot Experimental: Agricultural Edge Detection 🌍

[![Version](https://img.shields.io/badge/version-1.0.0-brightgreen)](https://github.com/your-repo)
[![Python](https://img.shields.io/badge/python-3.8%2B-blue)](https://www.python.org/)
[![Docker](https://img.shields.io/badge/docker-ready-blue)](https://www.docker.com/)
[![Kubernetes](https://img.shields.io/badge/Kubernetes-Deploy%20Ready-blue?logo=kubernetes&logoColor=white)](https://kubernetes.io/)
[![Jenkins](https://img.shields.io/badge/jenkins-automated-orange)](https://www.jenkins.io/)

Este repositorio contiene los scripts, análisis y configuraciones para desarrollar un flujo completo de **detección de bordes agrícolas** utilizando imágenes satelitales Sentinel-2, **modelos de segmentación automática (SAM)** y herramientas de análisis geoespacial avanzadas.

## Estructura del Proyecto

```plaintext
pilot_experimental/
├── analysis_statistics.html       # Análisis estadístico y métricas de los datos procesados.
├── api_prototype.py               # Prototipo de API para detección de bordes agrícolas.
├── dataset/                       # Datasets personalizados para el fine-tuning.
│   ├── train_annotations.json     # Anotaciones de entrenamiento (COCO).
│   ├── train_images/              # Imágenes de entrenamiento.
│   ├── val_annotations.json       # Anotaciones de validación (COCO).
│   └── val_images/                # Imágenes de validación.
├── diagrama.png                   # Diagrama del flujo de trabajo completo.
├── Dockerfile                     # Dockerfile para contenerizar el flujo.
├── final_check_integrity.py       # Verificación de integridad de archivos generados.
├── fine_tuning_sam.py             # Fine-tuning del modelo SAM.
├── generate_sobel_sentinel.py     # Procesamiento Sobel de imágenes Sentinel.
├── Jenkinsfile                    # Pipeline automatizado con Jenkins.
├── k8s-deployment.yaml            # Configuración de despliegue en Kubernetes.
├── ndvi_evi_analysis.html         # Análisis NDVI/EVI.
├── ndvi_evi_visualization_map.html # Mapa interactivo de NDVI/EVI.
├── puppet-manifest.pp             # Gestión de infraestructura con Puppet.
├── sam_2_apply_colored2.py        # Segmentación SAM con exportación a GeoJSON/GPKG.
├── sentinnel_download_script.py   # Descarga de imágenes Sentinel-2.
├── tech_specs.txt                 # Especificaciones técnicas del proyecto.
├── test site.kml                  # Áreas de interés definidas en formato KML.
├── unet_model.h5                  # Modelo UNet para futuras integraciones.
└── verificar_simetria.py          # Verificación de consistencia espacial.
```

<img src="diagrama.png" alt="Flujo de trabajo del proyecto" width="600"/>


## Funcionalidades

**Preprocesamiento** de Imágenes **Satelitales**:

Generación de mapas NDVI/EVI interactivos.
Procesamiento Sobel para detección de bordes.

**Segmentación** y **Fine-Tuning**:

Fine-tuning del modelo SAM con datasets personalizados.
Generación de máscaras RGBA exportadas en formatos GeoJSON y GPKG.
Automatización y Escalabilidad:

Pipeline automatizado con Jenkins.
Configuración lista para Kubernetes y Puppet.


**Análisis Geoespacial**:

Verificación de alineación espacial entre máscaras e imágenes originales.
Estadísticas y métricas exportadas en formato HTML.

**Prototipo de API**:

Servicio RESTful para integrar detección de bordes agrícolas en aplicaciones externas.



Este proyecto está abierto a contribuciones. Para más detalles, revisa **tech_specs.txt**

<img src="mascaras en google earth2.jpg" alt="mascaras geolocalizables" width="600"/>

``` bash
*alex_strange
```
