"""
sam_2_apply_colored2.py

Descripción:
Este script procesa máscaras generadas por Segment Anything Model (SAM) para incluir varias visualizaciones y formatos de salida:
1. Máscaras segmentadas con bordes delineados en amarillo.
2. Máscaras RGBA coloreadas con transparencia.
3. Archivos georreferenciados ajustados para análisis espacial.
4. Archivos GeoJSON para visualización y análisis interoperable.

Estructura de Entrada:
- Imágenes generadas previamente en formato TIFF con segmentaciones.
- Las imágenes deben contener información de georreferenciación.

Estructura de Salida:
- Máscaras con bordes delineados (archivos TIFF).
- Máscaras RGBA con transparencia (archivos TIFF).
- Archivos GPKG con atributos adicionales como área en acres y recuento de polígonos.
- Archivos GeoJSON derivados de los GPKG para visualización y análisis GIS.

Componentes principales:
1. Generación de bordes en amarillo para visualización.
2. Creación de máscaras RGBA con colores únicos y transparencia.
3. Ajuste y preservación de metadatos georreferenciados.
4. Generación de archivos GIS (GPKG, GeoJSON) para análisis espacial detallado.

Dependencias:
- Python >= 3.8
- NumPy
- OpenCV
- Rasterio
- Geopandas

alex_strange
"""


from samgeo import SamGeo
import os
import rasterio
import numpy as np
import geopandas as gpd
import cv2

# Configuración de SAM
sam = SamGeo(
    model_type="vit_h",
    checkpoint="sam_vit_h_4b8939.pth",
    device='cpu'  # Forzar uso de CPU
)

# Diccionario de parámetros para SAM
sam_params = {
    "batch": True,
    "foreground": True,
    "erosion_kernel": (5, 5),
    "mask_multiplier": 255,
    "multi_crop": False,
    "background": False
}

os.environ["CUDA_VISIBLE_DEVICES"] = "-1"  # Deshabilitar el uso de GPU

# Directorios
masks_base_dir = "masks/sentinel"
output_base_dir = "sam_output"
os.makedirs(output_base_dir, exist_ok=True)

# Listar las estaciones disponibles
seasons = ["initial", "refresh", "finalize"]
sobel_band = "B8"

# Lista de máscaras a regenerar
lista_regeneracion = ["Polygon_1_B8_mask.tif"]
#lista_regeneracion = []

# Función para preparar máscaras para SAM
def prepare_mask_for_sam(input_path):
    with rasterio.open(input_path) as src:
        mask = src.read(1)  # Leer solo la primera banda (2D array)
        meta = src.meta

        # Asegurar que la máscara sea 3D para SAM
        mask = np.expand_dims(mask, axis=-1)  # Expandir dimensiones: (H, W) -> (H, W, 1)
        mask = np.repeat(mask, 3, axis=-1)  # Repetir en canales RGB: (H, W, 1) -> (H, W, 3)

    return mask, meta

# Función para escribir salida inicial con metadatos correctos
def ensure_metadata(output_path, original_meta):
    """
    Asegura que los metadatos CRS y Transform se mantengan en el archivo de salida.
    """
    with rasterio.open(output_path, "r+") as dst:
        print(f"    Ajustando metadatos georreferenciados para {output_path}")
        dst.crs = original_meta["crs"]
        dst.transform = original_meta["transform"]

# Función para generar bordes amarillos con transparencia y guardarlos como TIFF
def add_yellow_borders_with_transparency(mask_path, output_borders_path):
    with rasterio.open(mask_path) as src:
        mask = src.read(1)
        meta = src.meta

    # Detectar bordes
    edges = cv2.Canny(mask, 50, 150)

    # Crear una matriz RGBA para incluir transparencia
    borders_yellow = np.zeros((mask.shape[0], mask.shape[1], 4), dtype=np.uint8)
    borders_yellow[edges > 0] = [255, 255, 0, 255]  # Amarillo sólido con opacidad completa
    borders_yellow[edges == 0, 3] = 0  # Fondo transparente

    # Actualizar metadatos para 4 canales (RGBA)
    meta.update({"count": 4, "dtype": "uint8"})

    # Guardar la máscara con bordes amarillos y transparencia
    with rasterio.open(output_borders_path, "w", **meta) as dst:
        for i in range(4):
            dst.write(borders_yellow[:, :, i], i + 1)

    print(f"    Bordes amarillos con transparencia guardados en: {output_borders_path}")


# Función para generar un archivo RGBA coloreado
def add_transparency_and_color(input_mask_path, output_rgba_path):
    with rasterio.open(input_mask_path) as src:
        mask = src.read(1)
        meta = src.meta

    alpha = np.where(mask > 0, 255, 0).astype(np.uint8)
    unique_values = np.unique(mask)
    color_map = {val: np.random.randint(0, 255, size=3) for val in unique_values if val > 0}
    color_mask = np.zeros((mask.shape[0], mask.shape[1], 3), dtype=np.uint8)
    for val, color in color_map.items():
        color_mask[mask == val] = color

    rgba_mask = np.dstack((color_mask, alpha))

    meta.update({"count": 4, "dtype": "uint8"})
    with rasterio.open(output_rgba_path, "w", **meta) as dst:
        for i in range(4):
            dst.write(rgba_mask[:, :, i], i + 1)

    print(f"    Máscara RGBA coloreada guardada en: {output_rgba_path}")

# Función para agregar atributos al archivo GPKG
def add_attributes_to_gpkg(gpkg_path):
    gdf = gpd.read_file(gpkg_path)
    if gdf.crs is None:
        print(f"Advertencia: CRS no definido en {gpkg_path}. Asignando 'EPSG:4326'.")
        gdf.set_crs("EPSG:4326", inplace=True)

    gdf_projected = gdf.to_crs(epsg=3857)
    gdf["Area_acres"] = gdf_projected.geometry.area * 0.000247105
    gdf["Polygon_Count"] = len(gdf)

    gdf.to_file(gpkg_path, driver="GPKG")
    print(f"Atributos agregados al archivo: {gpkg_path}")

# Función para generar GeoJSON
def generate_geojson(gpkg_path, geojson_path):
    gdf = gpd.read_file(gpkg_path)
    if gdf.crs is None:
        print(f"Advertencia: CRS no definido en {gpkg_path}. Asignando 'EPSG:4326'.")
        gdf.set_crs("EPSG:4326", inplace=True)

    gdf.to_file(geojson_path, driver="GeoJSON")
    print(f"GeoJSON generado: {geojson_path}")

# Procesar estaciones
for season in seasons:
    print(f"\nProcesando estación: {season}")
    masks_dir = os.path.join(masks_base_dir, season)
    output_dir = os.path.join(output_base_dir, season)
    os.makedirs(output_dir, exist_ok=True)

    files = [
        f for f in os.listdir(masks_dir)
        if f.endswith(".tif") and sobel_band in f
    ]

    if lista_regeneracion:
        files = [f for f in files if f in lista_regeneracion]

    for file_name in files:
        input_path = os.path.join(masks_dir, file_name)
        output_path = os.path.join(output_dir, file_name.replace(".tif", "_delineation.tif"))
        gpkg_path = output_path.replace(".tif", ".gpkg")
        geojson_path = output_path.replace(".tif", ".geojson")
        rgba_output_path = output_path.replace("_delineation.tif", "_rgba.tif")
        yellow_borders_path = output_path.replace("_delineation.tif", "_borders_yellow.tif")

        print(f"  Procesando archivo: {file_name}")

        try:
            # Preparar máscara y obtener metadatos originales
            prepared_mask, meta = prepare_mask_for_sam(input_path)

            # Procesar con SAM
            sam.generate(
                prepared_mask,
                output_path,
                batch=sam_params["batch"],
                foreground=sam_params["foreground"],
                erosion_kernel=sam_params["erosion_kernel"],
                mask_multiplier=sam_params["mask_multiplier"],
                multi_crop=sam_params["multi_crop"],
                background=sam_params["background"]
            )

            # Asegurar que las salidas tengan metadatos georreferenciados
            ensure_metadata(output_path, meta)

            # Generar bordes amarillos
            add_yellow_borders_with_transparency(output_path, yellow_borders_path)

            # Generar máscara RGBA coloreada
            add_transparency_and_color(output_path, rgba_output_path)

            # Convertir a GPKG y agregar atributos
            sam.tiff_to_gpkg(output_path, gpkg_path)
            add_attributes_to_gpkg(gpkg_path)

            # Generar GeoJSON
            generate_geojson(gpkg_path, geojson_path)

        except Exception as e:
            print(f"    Error procesando {file_name}: {e}")

print("Segmentación completada.")
