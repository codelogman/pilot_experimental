"""
api_prototype.py

Descripción:
Este script implementa un prototipo de API para la interacción con modelos de segmentación, específicamente SAM (Segment Anything Model). 
Proporciona funcionalidades para recibir imágenes, procesarlas utilizando SAM y devolver resultados como máscaras segmentadas, 
anotaciones o cualquier otra información relevante.

Estructura del Dataset (opcional, si aplica):
- La entrada incluye imágenes en formatos estándar (e.g., JPEG, PNG) junto con metadatos opcionales.
- Las salidas siguen el formato COCO RLE para máscaras, junto con información de calidad y estabilidad de las segmentaciones.

Funcionalidades principales:
1. Recepción de imágenes y parámetros mediante solicitudes HTTP.
2. Procesamiento de imágenes mediante SAM o modelos relacionados.
3. Respuesta con máscaras segmentadas y metadatos en formato JSON o binario.

Dependencias:
- Python >= 3.8
- Flask/FastAPI (o framework de API)
- SAM (Segment Anything Model)
- Pycocotools (para trabajar con COCO RLE)

alex_strange
"""


from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse, JSONResponse
import os
import glob

app = FastAPI()

# Directorios
output_base_dir = "sam_output"
gpkg_dir = "gpkg_files"  # Archivos vectoriales

# Endpoint: Listar polígonos procesados
@app.get("/polygons")
def list_polygons():
    polygons = []
    for season in ["initial", "refresh", "finalize"]:
        season_dir = os.path.join(output_base_dir, season)
        if not os.path.exists(season_dir):
            continue

        # Buscar archivos GPKG
        gpkg_files = glob.glob(os.path.join(season_dir, "*.gpkg"))
        for file in gpkg_files:
            polygons.append({
                "filename": os.path.basename(file),
                "season": season,
                "path": file
            })
    return {"polygons": polygons}

# Endpoint: Obtener detalles de un polígono
@app.get("/polygons/{polygon_id}")
def get_polygon_details(polygon_id: str):
    polygon_path = None
    for season in ["initial", "refresh", "finalize"]:
        season_dir = os.path.join(output_base_dir, season)
        potential_file = os.path.join(season_dir, f"{polygon_id}.gpkg")
        if os.path.exists(potential_file):
            polygon_path = potential_file
            break

    if not polygon_path:
        raise HTTPException(status_code=404, detail="Polígono no encontrado")

    # Leer metadatos del archivo GPKG
    import geopandas as gpd
    gdf = gpd.read_file(polygon_path)
    area_acres = gdf["Area_acres"].sum() if "Area_acres" in gdf.columns else None
    polygon_count = len(gdf)

    return {
        "polygon_id": polygon_id,
        "area_acres": area_acres,
        "polygon_count": polygon_count,
        "file_path": polygon_path
    }

# Endpoint: Descargar archivos generados
@app.get("/files/{filename}")
def download_file(filename: str):
    for season in ["initial", "refresh", "finalize"]:
        season_dir = os.path.join(output_base_dir, season)
        file_path = os.path.join(season_dir, filename)
        if os.path.exists(file_path):
            return FileResponse(file_path)
    raise HTTPException(status_code=404, detail="Archivo no encontrado")

# Endpoint: Iniciar procesamiento (placeholder)
@app.post("/process")
def process_new_area(area: dict):
    """
    Simula el inicio de un nuevo procesamiento.
    """
    # Por ahora, este endpoint no está implementado.
    return {"message": "Procesamiento iniciado (placeholder).", "area": area}

