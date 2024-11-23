import xml.etree.ElementTree as ET
import json

def extract_polygons_from_kml(kml_file_path):
    # Parse the KML file
    tree = ET.parse(kml_file_path)
    root = tree.getroot()
    
    # Define the namespace for KML
    namespace = {'kml': 'http://www.opengis.net/kml/2.2'}
    
    # Find all Polygon elements
    polygons = []
    for placemark in root.findall(".//kml:Placemark", namespace):
        coordinates = placemark.find(".//kml:coordinates", namespace)
        if coordinates is not None:
            # Extract coordinates as a list of [lat, lon] pairs
            raw_coords = coordinates.text.strip().split()
            polygon = [
                [float(coord.split(',')[1]), float(coord.split(',')[0])]  # Switch to [lat, lon]
                for coord in raw_coords
            ]
            polygons.append(polygon)
    return polygons

def save_polygons_to_json(polygons, json_file_path):
    # Save the polygons to a JSON file
    with open(json_file_path, 'w') as f:
        json.dump(polygons, f, indent=4)

def load_polygons_from_json(json_file_path):
    # Load the polygons from a JSON file
    with open(json_file_path, 'r') as f:
        polygons = json.load(f)
    return polygons

# Ruta del archivo KML
kml_file_path = 'test site.kml'  # Cambia esta ruta al archivo KML
# Ruta para guardar los polígonos
json_file_path = 'polygons.json'

# Extraer y guardar polígonos
polygons = extract_polygons_from_kml(kml_file_path)
save_polygons_to_json(polygons, json_file_path)

print(f"Polygons saved to {json_file_path}.")

# Prueba: cargar polígonos y mostrarlos
loaded_polygons = load_polygons_from_json(json_file_path)
for i, polygon in enumerate(loaded_polygons):
    print(f"Polygon {i+1}:")
    print(polygon)
    print()

