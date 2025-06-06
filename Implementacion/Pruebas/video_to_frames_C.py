import cv2
import os
import glob
from tqdm import tqdm
import threading

def process_video(video_path, output_folder, position):
    video_name = os.path.splitext(os.path.basename(video_path))[0]
    video_output_folder = os.path.join(output_folder, video_name)
    os.makedirs(video_output_folder, exist_ok=True)

    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        print(f"⚠️ Error al abrir video: {video_path}, saltando...")
        return

    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    frame_count = 0
    sampling_rate = 30

    '''
    El objetivo es calcular 1 frame cada 0.5 segundos ya que es un buen balance entre densidad y eficiencia
    Por lo tanto -> 60fps * 0.5 = 30 sampling_rate
    '''

    with tqdm(
        total=total_frames,
        desc=f"Extrayendo {video_name[:15]}...",
        unit="frame",
        position=position,  # Posición única para cada barra
        leave=False  # Elimina las barras al finalizar
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
    # Mensaje final fuera de la barra de progreso
    print(f"✅ {video_name[:15]} ({frame_count} frames)")

if __name__ == "__main__":
    current_dir = os.path.dirname(os.path.abspath(__file__))
    two_folders_up = os.path.abspath(os.path.join(current_dir, "../../"))
    video_dir = os.path.join(two_folders_up, "Videos")

    if not os.path.exists(video_dir):
        raise FileNotFoundError(f"⚠️ Carpeta de videos no encontrada: {video_dir}")

    output_folder = os.path.join(current_dir, "frames/")
    os.makedirs(output_folder, exist_ok=True)

    video_files = glob.glob(os.path.join(video_dir, "*.mp4"))
    if not video_files:
        print("⚠️ No se encontraron videos MP4 en la carpeta")
        exit()

    # Crear un hilo por video con posición única
    threads = []
    for idx, video in enumerate(video_files):
        t = threading.Thread(
            target=process_video,
            args=(video, output_folder, idx)
        )
        threads.append(t)
        t.start()

    # Esperar a que todos los hilos terminen
    for t in threads:
        t.join()

    print("\n✅ Proceso completado para todos los videos!")