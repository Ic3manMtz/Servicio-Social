import cv2
import numpy as np
from sklearn.cluster import DBSCAN
import os

def get_boxes_from_txt(txt_path, img_width, img_height):
    # Leer coordenadas YOLO del archivo de etiquetas
    boxes = []
    with open(txt_path, 'r') as f:
        for line in f:
            class_id, x_center, y_center, w, h = map(float, line.split())
            # Convertir a píxeles
            x = int((x_center - w/2) * img_width)
            y = int((y_center - h/2) * img_height)
            w = int(w * img_width)
            h = int(h * img_height)
            boxes.append((x, y, w, h))
    return boxes

def draw_groups(image, groups):
    # Colores aleatorios para cada grupo
    colors = np.random.randint(0, 255, size=(len(groups), 3), dtype=np.uint8)
    for i, (group_id, boxes) in enumerate(groups.items()):
        if group_id == -1:  # Ignorar outliers (personas no agrupadas)
            continue
        # Dibujar bounding box del grupo
        x_min = min([x for (x, y, w, h) in boxes])
        y_min = min([y for (x, y, w, h) in boxes])
        x_max = max([x + w for (x, y, w, h) in boxes])
        y_max = max([y + h for (x, y, w, h) in boxes])
        cv2.rectangle(image, (x_min, y_min), (x_max, y_max), colors[i].tolist(), 2)
        cv2.putText(image, f"Grupo {i}", (x_min, y_min - 10),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, colors[i].tolist(), 2)
    return image

# Carpeta principal con detecciones (contiene subcarpetas por video)
detections_root = "resultados/detections/"
output_root = "resultados/groups/"

# Recorrer cada subcarpeta (cada video)
for video_folder in os.listdir(detections_root):
    video_path = os.path.join(detections_root, video_folder)
    if not os.path.isdir(video_path):
        continue
    
    # Crear carpeta de salida correspondiente
    output_video_folder = os.path.join(output_root, video_folder)
    os.makedirs(output_video_folder, exist_ok=True)
    
    # Procesar cada frame en la subcarpeta
    for frame_file in os.listdir(video_path):
        if not frame_file.endswith(".jpg"):
            continue
            
        # Cargar imagen y anotaciones YOLO
        img_path = os.path.join(video_path, frame_file)
        txt_path = img_path.replace(".jpg", ".txt")
        
        # Verificar que exista el archivo de texto
        if not os.path.exists(txt_path):
            continue
            
        image = cv2.imread(img_path)
        if image is None:
            continue
            
        img_height, img_width = image.shape[:2]
        
        # Obtener cajas de personas detectadas
        boxes = get_boxes_from_txt(txt_path, img_width, img_height)
        
        # Detectar grupos usando DBSCAN
        if len(boxes) > 0:
            centers = np.array([[(x + w//2), (y + h//2)] for (x, y, w, h) in boxes])
            clustering = DBSCAN(eps=100, min_samples=2).fit(centers)  # Ajusta "eps" según la proximidad
            groups = {}
            for idx, label in enumerate(clustering.labels_):
                if label not in groups:
                    groups[label] = []
                groups[label].append(boxes[idx])
            
            # Dibujar grupos en la imagen
            image = draw_groups(image, groups)
        
        # Guardar imagen con grupos
        output_path = os.path.join(output_video_folder, frame_file)
        cv2.imwrite(output_path, image)

print("✅ Grupos detectados y guardados en estructura de carpetas en 'resultados/groups/'")