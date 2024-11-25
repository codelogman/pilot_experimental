# Agricultural Field Border Detection

## Descripción

Este repositorio contiene todos los scripts, datos y notebooks necesarios para detectar y analizar automáticamente bordes agrícolas mediante imágenes satelitales (Landsat y Sentinel). Se emplean índices de vegetación como NDVI y EVI, junto con algoritmos de detección de bordes.

---

## Estructura del Proyecto

```plaintext

pilot_experimental/
├── analysis_statistics.html       # Statistical analysis and metrics for the processed data.
├── api_prototype.py               # Prototype implementation of an API for integrating field border detection services.
├── dataset/                       # Directory containing datasets for fine-tuning SAM.
│   ├── train_annotations.json     # Training dataset annotations in COCO format.
│   ├── train_images/              # Directory containing training images.
│   ├── val_annotations.json       # Validation dataset annotations in COCO format.
│   └── val_images/                # Directory containing validation images.
├── diagrama.png                   # Diagram illustrating the complete workflow, including API and fine-tuning integration.
├── Dockerfile                     # Dockerfile to containerize the workflow and dependencies.
├── final_check_integrity.py       # Script to ensure final integrity of generated files and outputs.
├── fine_tuning_sam.py             # Script for fine-tuning the SAM model using custom datasets.
├── generate_sobel_sentinel.py     # Script to process Sentinel images using Sobel edge detection for field segmentation enhancement.
├── Jenkinsfile                    # Jenkinsfile for automating pipeline deployment and testing.
├── k8s-deployment.yaml            # Kubernetes deployment configuration for scalable API and workflow deployment.
├── ndvi_evi_analysis.html         # Detailed NDVI and EVI analysis generated from Sentinel images.
├── ndvi_evi_visualization_map.html # Interactive map for visualizing NDVI and EVI values across polygons.
├── puppet-manifest.pp             # Puppet configuration file for managing infrastructure provisioning.
├── sam_2_apply_colored2.py        # Script to apply SAM segmentation, generate RGBA masks, and export GPKG/GeoJSON.
├── sentinnel_download_script.py   # Script to download Sentinel-2 satellite imagery based on polygonal areas defined in the input KML file.
├── tech_specs.txt                 # Technical documentation detailing the workflow, methodologies, and compliance with RFP requirements.
├── test site.kml                  # Input KML file defining the polygonal areas of interest for field border detection.
├── unet_model.h5                  # Placeholder for a future UNet model file, intended for potential integration.
└── verificar_simetria.py          # Script to verify spatial alignment and consistency between original images and generated masks.
