import cv2
import os
import glob
from tqdm import tqdm

# Obtener la ruta del directorio actual del script
current_dir = os.path.dirname(os.path.abspath(__file__))

# Configuración de rutas
two_folders_up = os.path.abspath(os.path.join(current_dir, "../../"))
video_dir = os.path.join(two_folders_up, "Videos")  # Carpeta con videos

# Verificar si existe la carpeta de videos
if not os.path.exists(video_dir):
    raise FileNotFoundError(f"⚠️ Carpeta de videos no encontrada: {video_dir}")

# Crear carpeta base para frames
output_folder = os.path.join(current_dir, "frames/")
os.makedirs(output_folder, exist_ok=True)

# Encontrar todos los archivos MP4 en la carpeta de videos
video_files = glob.glob(os.path.join(video_dir, "*.mp4"))

if not video_files:
    print("⚠️ No se encontraron videos MP4 en la carpeta")
    exit()

for video_path in video_files:
    # Crear subcarpeta para el video actual
    video_name = os.path.splitext(os.path.basename(video_path))[0]
    video_output_folder = os.path.join(output_folder, video_name)
    os.makedirs(video_output_folder, exist_ok=True)

    # Inicializar captura de video
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        print(f"⚠️ Error al abrir video: {video_path}, saltando...")
        continue

    # Configurar parámetros de extracción
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    frame_count = 0
    sampling_rate = 30 

    '''
    El objetivo es calcular 1 frame cada 0.5 segundos ya que es un buen balance entre densidad y eficiencia
    Por lo tanto -> 60fps * 0.5 = 30 sampling_rate
    '''

    # Procesar con barra de progreso
    with tqdm(
        total=total_frames, 
        desc=f"Extrayendo {video_name[:15]}...", 
        unit="frame"
    ) as pbar:
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            
            if frame_count % sampling_rate == 0:
                frame_file = os.path.join(
                    video_output_folder, 
                    f"frame_{frame_count:06d}.jpg"
                )
                cv2.imwrite(frame_file, frame)
            
            frame_count += 1
            pbar.update(1)

    cap.release()
    print(f"✅ {frame_count} frames extraídos en: {video_output_folder}")

print("\nProceso completado para todos los videos!")