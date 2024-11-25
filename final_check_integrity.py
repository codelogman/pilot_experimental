import numpy as np

# Cargar los datos
X_data_path = "training_data/X_data.npy"
Y_data_path = "training_data/Y_data.npy"

print("Cargando los datasets...")
X = np.load(X_data_path)
Y = np.load(Y_data_path)

# Verificar dimensiones
print(f"Dimensiones de X: {X.shape}")
print(f"Dimensiones de Y: {Y.shape}")

# Asegurarse de que las imágenes y máscaras sean de escala de grises
if len(X.shape) == 3:
    print("Las imágenes tienen 3 dimensiones. Agregando canal de color...")
    X = np.expand_dims(X, axis=-1)

if len(Y.shape) == 3:
    print("Las máscaras tienen 3 dimensiones. Agregando canal de color...")
    Y = np.expand_dims(Y, axis=-1)

# Validar valores de las imágenes
if X.min() < 0 or X.max() > 1:
    print(f"Advertencia: Las imágenes no están normalizadas. Valores: Min {X.min()}, Max {X.max()}")
else:
    print("Las imágenes están normalizadas entre 0 y 1.")

# Validar valores de las máscaras
mask_values = np.unique(Y)
if np.array_equal(mask_values, [0, 1]):
    print("Las máscaras son binarias (valores: 0 y 1).")
else:
    print(f"Advertencia: Las máscaras no son binarias. Valores únicos encontrados: {mask_values}")

# Verificar si las dimensiones de entrada son consistentes
if X.shape[:-1] != Y.shape[:-1]:
    print("Error: Las dimensiones de las imágenes y máscaras no coinciden.")
else:
    print("Dimensiones de imágenes y máscaras son consistentes.")

# Guardar los datos corregidos si es necesario
np.save(X_data_path, X)
np.save(Y_data_path, Y)
print("Datos validados y guardados nuevamente (si fue necesario).")

