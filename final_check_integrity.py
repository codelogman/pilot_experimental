import os
import csv
import rasterio
import numpy as np
import geopandas as gpd
from pyproj import CRS

# Directorio de datos generados
output_base_dir = "sam_output"
csv_output_path = "integrity_check_results.csv"

# Columnas para el archivo CSV
csv_columns = [
    "file_name",
    "file_type",
    "width",
    "height",
    "crs",
    "transform",
    "Legal_Land_Description",
    "Polygon_Count",
    "Area_acres",
    "processing_time",
    "mapped_date",
    "image_source",
    "notes"
]

# Función para verificar un archivo TIFF
def check_tiff(file_path):
    with rasterio.open(file_path) as src:
        width = src.width
        height = src.height
        crs = src.crs
        transform = src.transform
    return {
        "width": width,
        "height": height,
        "crs": crs.to_string() if crs else "None",
        "transform": str(transform)  # Convertir a string para evitar errores
    }

# Función para verificar un archivo GPKG
def check_gpkg(file_path):
    gdf = gpd.read_file(file_path)
    if gdf.crs:
        crs = gdf.crs.to_string()
    else:
        crs = "None"
    
    polygon_count = len(gdf)
    area_acres = gdf["Area_acres"].sum() if "Area_acres" in gdf.columns else "N/A"
    lld = gdf["Legal_Land_Description"].iloc[0] if "Legal_Land_Description" in gdf.columns else "Pending to revision"
    mapped_date = gdf["Mapped_Date"].iloc[0] if "Mapped_Date" in gdf.columns else "Unknown"
    image_source = gdf["Image_Source"].iloc[0] if "Image_Source" in gdf.columns else "Unknown"

    return {
        "crs": crs,
        "Polygon_Count": polygon_count,
        "Area_acres": area_acres,
        "Legal_Land_Description": lld,
        "mapped_date": mapped_date,
        "image_source": image_source
    }

# Crear CSV con resultados
with open(csv_output_path, mode='w', newline='') as csv_file:
    writer = csv.DictWriter(csv_file, fieldnames=csv_columns)
    writer.writeheader()

    # Iterar por las estaciones y archivos generados
    for season in ["initial", "refresh", "finalize"]:
        season_dir = os.path.join(output_base_dir, season)
        if not os.path.exists(season_dir):
            continue

        for file_name in os.listdir(season_dir):
            file_path = os.path.join(season_dir, file_name)
            row = {key: "" for key in csv_columns}  # Inicializar todas las columnas
            row.update({
                "file_name": file_name,
                "file_type": file_name.split(".")[-1],
            })

            try:
                if file_name.endswith(".tif"):
                    # Validar archivos TIFF
                    tiff_info = check_tiff(file_path)
                    row.update(tiff_info)
                elif file_name.endswith(".gpkg"):
                    # Validar archivos GPKG
                    gpkg_info = check_gpkg(file_path)
                    row.update(gpkg_info)
                else:
                    row["notes"] = "File type not recognized for validation."

            except Exception as e:
                row["notes"] = f"Error during validation: {e}"

            # Filtrar claves de `row` para que coincidan con `csv_columns`
            filtered_row = {key: row.get(key, "") for key in csv_columns}
            writer.writerow(filtered_row)

print(f"Integridad revisada. Resultados guardados en {csv_output_path}.")

