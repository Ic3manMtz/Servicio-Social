import cv2
import os
from tqdm import tqdm  # <-- Importar la biblioteca

# Obtener la ruta del directorio actual del script
current_dir = os.path.dirname(os.path.abspath(__file__))

# Configuración de rutas
two_folders_up = os.path.abspath(os.path.join(current_dir, "../../"))  # 2 carpetas arriba

video_path = os.path.join(two_folders_up, "Videos", "05-02-2025-V1.mp4")  # <-- Ajusta nombres

# Verificar si existe el video
if not os.path.exists(video_path):
    raise FileNotFoundError(f"⚠️ Archivo no encontrado: {video_path}")

# Crear carpeta de salida
output_folder = os.path.join(current_dir, "frames/")
os.makedirs(output_folder, exist_ok=True)

# Extraer frames
cap = cv2.VideoCapture(video_path)

# Verificar si el video se abrió correctamente
if not cap.isOpened():
    raise Exception("Error al abrir el video")

# Obtener el total de frames del video
total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
frame_count = 0
sampling_interval = 4 # 60 FPS / FPS objetivo =  sampling_interval
'''
Alta precisión  30-15 FPS   2-4 frames
Balanceado      15-10 FPS   4-6 frames
Liviano         10-2 FPS    6-12 frames
'''

# Configurar barra de progreso
with tqdm(total=total_frames, desc="Extrayendo frames", unit="frame") as pbar:
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break
        # Guardar frame cada 0.5 segundos
        if frame_count % 15 == 0:  # 30 FPS -> 15 frames = 0.5 segundos
            cv2.imwrite(f"{output_folder}frame_{frame_count:04d}.jpg", frame)
        frame_count += 1
        pbar.update(1)  # Actualizar barra

cap.release()
print(f"\n✅ {frame_count} frames extraídos en {output_folder}")