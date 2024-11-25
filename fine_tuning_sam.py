"""
fine_tuning_sam.py

Descripción:
Este script está diseñado para realizar el ajuste fino (fine-tuning) del modelo Segment Anything (SAM) utilizando un dataset personalizado.
El entrenamiento aprovecha el modelo preentrenado de SAM y ajusta sus pesos para optimizar su rendimiento en tareas de segmentación específicas.

Estructura del Dataset:
- Las imágenes y anotaciones se estructuran en un formato compatible con el protocolo COCO.
- Cada entrada del dataset incluye:
  - `image`: Información de la imagen, como dimensiones y nombre del archivo.
  - `annotations`: Lista de máscaras asociadas con sus propiedades (segmentation, bbox, área, etc.).

Componentes principales:
1. Carga del modelo preentrenado de SAM.
2. Configuración del optimizador y la política de aprendizaje.
3. Loop de entrenamiento para ajustar los pesos del modelo.
4. Evaluación del modelo en un conjunto de validación.

Dependencias:
- Python >= 3.8
- PyTorch
- Segment Anything (SAM) Framework
- pycocotools (para manejo del formato COCO)

alex_strange
"""


import torch
import torchvision
from torch.utils.data import DataLoader
from samgeo import SamGeo

# Configuración del modelo
sam = SamGeo(
    model_type="vit_h",
    checkpoint="sam_vit_h_4b8939.pth",
    device="cuda" if torch.cuda.is_available() else "cpu"
)

# Cargar dataset en formato COCO
from torchvision.datasets import CocoDetection
from torchvision.transforms import Compose, ToTensor, Normalize

# Transformaciones
transform = Compose([
    ToTensor(),
    Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])  # Normalización estándar
])

# Dataset
train_dataset = CocoDetection(
    root="path/to/images",
    annFile="path/to/annotations.json",
    transform=transform
)

val_dataset = CocoDetection(
    root="path/to/images",
    annFile="path/to/val_annotations.json",
    transform=transform
)

# DataLoader
train_loader = DataLoader(train_dataset, batch_size=4, shuffle=True, num_workers=4)
val_loader = DataLoader(val_dataset, batch_size=4, shuffle=False, num_workers=4)

# Congelar capas inferiores y ajustar las superiores
for param in sam.model.backbone.parameters():
    param.requires_grad = False

# Configurar optimizador y pérdida
optimizer = torch.optim.AdamW(filter(lambda p: p.requires_grad, sam.model.parameters()), lr=1e-4)
criterion = torch.nn.BCELoss()

# Entrenamiento
for epoch in range(10):  # Número de épocas
    sam.model.train()
    for images, targets in train_loader:
        images = images.to(sam.device)
        masks = [t["segmentation"] for t in targets]  # Obtener máscaras
        masks = torch.stack([torch.tensor(m) for m in masks]).to(sam.device)

        optimizer.zero_grad()
        outputs = sam.model(images)
        loss = criterion(outputs, masks)
        loss.backward()
        optimizer.step()
    print(f"Época {epoch}: Pérdida {loss.item()}")

# Guardar checkpoint
torch.save(sam.model.state_dict(), "sam_finetuned.pth")

