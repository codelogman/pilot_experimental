import matplotlib.pyplot as plt
import json

def visualize_polygons(polygons):
    for polygon in polygons:
        lon, lat = zip(*polygon)  # Separar longitudes y latitudes
        plt.plot(lon, lat)       # Dibujar el polígono
    plt.xlabel('Longitude')
    plt.ylabel('Latitude')
    plt.title('Visualización de Polígonos')
    plt.show()

def load_polygons_from_json(json_file_path):
    # Load the polygons from a JSON file
    with open(json_file_path, 'r') as f:
        polygons = json.load(f)
    return polygons
    
# Cargar y visualizar
polygons = load_polygons_from_json('polygons.json')
visualize_polygons(polygons)
