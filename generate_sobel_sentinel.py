import os
import cv2
import numpy as np
import rasterio
from rasterio.transform import from_origin
from multiprocessing import Pool

# Directorios de entrada y salida
sentinel_dir = "sentinel_img"
masks_dir = "masks/sentinel"
seasons = ["initial", "refresh", "finalize"]
bands = ["B8", "B4", "B3", "B2"]

# Crear directorios de salida para cada temporada
for season in seasons:
    os.makedirs(os.path.join(masks_dir, season), exist_ok=True)

# Función para cargar una banda
def load_band(filepath):
    with rasterio.open(filepath) as src:
        band = src.read(1).astype(np.float32)
        meta = src.meta
    return band, meta

# Sobel Ajustado
def apply_sobel(image):
    grad_x = cv2.Sobel(image, cv2.CV_64F, 1, 0, ksize=3)
    grad_y = cv2.Sobel(image, cv2.CV_64F, 0, 1, ksize=3)
    sobel = cv2.magnitude(grad_x, grad_y)
    sobel_normalized = cv2.normalize(sobel, None, 0, 255, cv2.NORM_MINMAX).astype(np.uint8)
    return sobel_normalized

# Resaltar líneas
def enhance_lines(image, kernel_size=3):
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (kernel_size, kernel_size))
    dilated = cv2.dilate(image, kernel, iterations=1)
    return dilated

# Aumentar contraste local
def local_contrast_enhancement(image, clip_limit=2.0, tile_grid_size=(8, 8)):
    clahe = cv2.createCLAHE(clipLimit=clip_limit, tileGridSize=tile_grid_size)
    enhanced = clahe.apply(image)
    return enhanced

# Validar máscaras
def validate_mask(mask):
    total_pixels = mask.size
    border_pixels = np.sum(mask > 0)
    border_coverage = (border_pixels / total_pixels) * 100
    return border_coverage >= 10  # Ejemplo: Umbral de 10% de cobertura

# Procesar un solo archivo
def process_file(args):
    season_input_dir, season_output_dir, file_name = args
    input_path = os.path.join(season_input_dir, file_name)
    output_path = os.path.join(season_output_dir, file_name.replace(".tif", "_mask.tif"))

    print(f"Procesando {file_name}...")

    try:
        band, meta = load_band(input_path)
        band_normalized = cv2.normalize(band, None, 0, 255, cv2.NORM_MINMAX).astype(np.uint8)
        sobel_result = apply_sobel(band_normalized)
        enhanced_lines = enhance_lines(sobel_result, kernel_size=3)
        final_enhanced = local_contrast_enhancement(enhanced_lines)

        # Validar máscara
        if not validate_mask(final_enhanced):
            print(f"Advertencia: Máscara {file_name} podría no tener bordes suficientes.")

        # Guardar máscara procesada con georreferenciación
        meta.update({"count": 1, "dtype": "uint8"})
        with rasterio.open(output_path, "w", **meta) as dst:
            dst.write(final_enhanced, 1)

        print(f"Mascara generada y guardada: {output_path}")
    except Exception as e:
        print(f"Error procesando {file_name}: {e}")

# Procesar por temporada con multiprocessing
for season in seasons:
    season_input_dir = os.path.join(sentinel_dir, season)
    season_output_dir = os.path.join(masks_dir, season)
    files = [
        f for f in os.listdir(season_input_dir)
        if any(band in f for band in bands) and f.endswith(".tif")
    ]

    # Crear argumentos para multiprocessing
    args = [(season_input_dir, season_output_dir, file_name) for file_name in files]

    # Procesar en paralelo
    with Pool() as pool:
        pool.map(process_file, args)

print("Generación de máscaras completada.")

