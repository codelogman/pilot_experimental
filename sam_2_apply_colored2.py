from samgeo import SamGeo
import os
import rasterio
import numpy as np
import cv2
import geopandas as gpd

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
    "erosion_kernel": (4, 4),
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

# Lista de máscaras a regenerar (si está vacía, se procesan todas las máscaras)
lista_regeneracion = []  # Ejemplo: ["Polygon_1_B8_mask.tif", "Polygon_3_B8_mask.tif"]

# Función para verificar dimensiones y ajustar
def prepare_mask_for_sam(input_path):
    with rasterio.open(input_path) as src:
        mask = src.read(1)
        mask = np.expand_dims(mask, axis=-1)
        mask = np.repeat(mask, 3, axis=-1)
        return mask

# Función para agregar atributos al archivo GPKG
def add_attributes_to_gpkg(gpkg_path):
    """
    Calcula atributos adicionales (área en acres, métricas) y los agrega al archivo GPKG.
    """
    gdf = gpd.read_file(gpkg_path)

    # Calcular área en acres
    gdf["Area_acres"] = gdf.geometry.area * 0.000247105  # Conversión a acres

    # Agregar métricas adicionales (ejemplo: número total de polígonos)
    gdf["Polygon_Count"] = len(gdf)  # Número total de polígonos

    # Guardar archivo con los atributos agregados
    gdf.to_file(gpkg_path, driver="GPKG")
    print(f"Atributos agregados al archivo: {gpkg_path}")

# Función para generar bordes amarillos y guardarlos como TIFF
def add_yellow_borders(mask_path, output_borders_path):
    with rasterio.open(mask_path) as src:
        mask = src.read(1)
        meta = src.meta

    # Detectar bordes
    edges = cv2.Canny(mask, 50, 150)

    # Crear una máscara amarilla (canales R, G, B)
    borders_yellow = np.zeros((mask.shape[0], mask.shape[1], 3), dtype=np.uint8)
    borders_yellow[edges > 0] = [255, 255, 0]  # Amarillo para bordes

    # Guardar como TIFF con georreferenciación
    meta.update({"count": 3, "dtype": "uint8"})
    with rasterio.open(output_borders_path, "w", **meta) as dst:
        for i in range(3):
            dst.write(borders_yellow[:, :, i], i + 1)

    print(f"    Bordes amarillos guardados en: {output_borders_path}")

# Función para generar un archivo RGBA coloreado
def add_transparency_and_color(input_mask_path, output_rgba_path):
    with rasterio.open(input_mask_path) as src:
        mask = src.read(1)
        meta = src.meta

    # Crear canal alfa: fondo transparente (0), áreas segmentadas opacas (255)
    alpha = np.where(mask > 0, 255, 0).astype(np.uint8)

    # Generar colores únicos para cada área segmentada
    unique_values = np.unique(mask)
    color_map = {val: np.random.randint(0, 255, size=3) for val in unique_values if val > 0}
    color_mask = np.zeros((mask.shape[0], mask.shape[1], 3), dtype=np.uint8)
    for val, color in color_map.items():
        color_mask[mask == val] = color

    # Combinar color y transparencia
    rgba_mask = np.dstack((color_mask, alpha))

    # Guardar como TIFF con georreferenciación
    meta.update({"count": 4, "dtype": "uint8"})
    with rasterio.open(output_rgba_path, "w", **meta) as dst:
        for i in range(4):
            dst.write(rgba_mask[:, :, i], i + 1)

    print(f"    Máscara RGBA coloreada guardada en: {output_rgba_path}")

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

    # Filtrar las máscaras si lista_regeneracion no está vacía
    if lista_regeneracion:
        files = [f for f in files if f in lista_regeneracion]

    for file_name in files:
        input_path = os.path.join(masks_dir, file_name)
        output_path = os.path.join(output_dir, file_name.replace(".tif", "_delineation.tif"))
        rgba_output_path = output_path.replace("_delineation.tif", "_rgba.tif")
        yellow_borders_path = output_path.replace("_delineation.tif", "_borders_yellow.tif")

        print(f"  Procesando archivo: {file_name}")

        try:
            prepared_mask = prepare_mask_for_sam(input_path)

            # Generar segmentación usando SAM
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

            # Convertir a GPKG
            vector_path = output_path.replace(".tif", ".gpkg")
            sam.tiff_to_gpkg(output_path, vector_path)

            # Agregar atributos al archivo GPKG
            add_attributes_to_gpkg(vector_path)

            # Generar bordes amarillos como TIFF
            add_yellow_borders(output_path, yellow_borders_path)

            # Generar máscara RGBA coloreada como TIFF
            add_transparency_and_color(output_path, rgba_output_path)

        except Exception as e:
            print(f"    Error procesando {file_name}: {e}")

print("Segmentación completada.")

