from ultralytics import YOLO
import os
from tqdm import tqdm  # <-- Librería para barras de progreso

# Cargar modelo YOLOv8
model = YOLO("yolov8n.pt")

# Ruta base de frames y proyecto de salida
base_frames_dir = "frames"
output_project = "resultados"

# Procesar cada subcarpeta dentro de 'frames'
for video_folder in tqdm(os.listdir(base_frames_dir), desc="Procesando videos"):
    video_folder_path = os.path.join(base_frames_dir, video_folder)
    
    if os.path.isdir(video_folder_path):
        # Contar frames para progreso individual
        frames = os.listdir(video_folder_path)
        total_frames = len(frames)
        
        # Ejecutar predicción con barra de progreso para este video
        for _ in model.predict(
            source=video_folder_path,
            conf=0.6,
            save=True,
            classes=[0],
            project=output_project,
            name=f"detections/{video_folder}",
            verbose=False,
            stream=True  # <-- Modo streaming para iteración
        ):
            # Actualizar barra de progreso por frame
            if 'pbar' not in locals():
                pbar = tqdm(total=total_frames, desc=f'Frames de {video_folder}', leave=False)
            pbar.update(1)
        
        if 'pbar' in locals():
            pbar.close()
            del pbar

print(f"\n✅ Detecciones guardadas en '{output_project}/detections/'")