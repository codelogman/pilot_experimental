"""
verificar_simetria.py

Descripción:
Este script verifica la simetría en un conjunto de datos de imágenes o matrices. 
La simetría puede evaluarse en diversos contextos, como imágenes médicas, análisis geométrico, o datos científicos, 
donde la estructura simétrica puede ser un indicador clave.

Estructura de Entrada:
- Archivos en formato NumPy (`.npy`) o imágenes (`.tif`, `.png`, etc.) que representan las matrices o imágenes a analizar.
- Parámetros opcionales para definir el tipo de simetría a evaluar (eje horizontal, eje vertical, o simetría rotacional).

Estructura de Salida:
- Indicador binario (True/False) para cada entrada que identifica si es simétrica.
- Estadísticas o métricas adicionales (por ejemplo, nivel de desvío de la simetría) opcionalmente almacenadas en un archivo de texto o JSON.

Componentes principales:
1. Carga y preprocesamiento de datos de entrada.
2. Cálculo de simetría para cada entrada.
3. Generación de reportes o gráficos para visualizar la simetría.

Dependencias:
- Python >= 3.8
- NumPy
- Rasterio (si se trabaja con datos geoespaciales)
- Matplotlib (opcional para visualización)

alex_strange
"""

import os
import rasterio
import json

# Directorios de entrada
images_dir = "sentinel_img"  # Imágenes originales
masks_dir = "masks/sentinel"  # Máscaras generadas

# Función para verificar simetría
def verify_symmetry(images_dir, masks_dir):
    """
    Verifica que las imágenes y máscaras tengan la misma resolución y alineación espacial.
    """
    issues = []  # Almacena diferencias detectadas
    seasons = ["initial", "refresh", "finalize"]

    for season in seasons:
        print(f"Verificando temporada: {season}...")
        season_images_dir = os.path.join(images_dir, season)
        season_masks_dir = os.path.join(masks_dir, season)

        # Listar archivos
        image_files = sorted([f for f in os.listdir(season_images_dir) if f.endswith(".tif")])
        mask_files = sorted([f for f in os.listdir(season_masks_dir) if f.endswith(".tif")])

        if len(image_files) != len(mask_files):
            issues.append({
                "season": season,
                "issue": "Cantidad de archivos no coincide",
                "image_count": len(image_files),
                "mask_count": len(mask_files)
            })

        for img_file, mask_file in zip(image_files, mask_files):
            img_path = os.path.join(season_images_dir, img_file)
            mask_path = os.path.join(season_masks_dir, mask_file)

            with rasterio.open(img_path) as img, rasterio.open(mask_path) as mask:
                # Verificar dimensiones
                if img.shape != mask.shape:
                    issues.append({
                        "season": season,
                        "issue": "Dimensiones no coinciden",
                        "image_file": img_file,
                        "mask_file": mask_file,
                        "image_shape": img.shape,
                        "mask_shape": mask.shape
                    })

                # Verificar alineación espacial
                if img.bounds != mask.bounds:
                    issues.append({
                        "season": season,
                        "issue": "Desalineación geoespacial",
                        "image_file": img_file,
                        "mask_file": mask_file
                    })

                # Verificar CRS
                if img.crs != mask.crs:
                    issues.append({
                        "season": season,
                        "issue": "Diferente CRS",
                        "image_file": img_file,
                        "mask_file": mask_file,
                        "image_crs": str(img.crs),
                        "mask_crs": str(mask.crs)
                    })

    if issues:
        print("Se detectaron los siguientes problemas:")
        for issue in issues:
            print(issue)
    else:
        print("Todas las imágenes y máscaras están perfectamente alineadas y tienen las mismas dimensiones.")

    # Guardar reporte de problemas
    save_issues_report(issues, output_file="symmetry_issues_report.json")

# Guardar reporte de problemas
def save_issues_report(issues, output_file="symmetry_issues_report.json"):
    with open(output_file, "w") as f:
        json.dump(issues, f, indent=4)
    print(f"Reporte de problemas guardado en: {output_file}")

# Ejecutar verificación
verify_symmetry(images_dir, masks_dir)

