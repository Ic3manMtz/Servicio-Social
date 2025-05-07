import os
import glob
import subprocess
from tqdm import tqdm
import threading

def get_total_frames(video_path):
    """Obtiene el número total de frames usando FFprobe"""
    cmd = [
        'ffprobe',
        '-v', 'error',
        '-select_streams', 'v:0',
        '-show_entries', 'stream=nb_frames',
        '-of', 'default=nokey=1:noprint_wrappers=1',
        video_path
    ]
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        return int(result.stdout.strip())
    except (subprocess.CalledProcessError, ValueError):
        return None

def process_video(video_path, output_folder, position):
    video_name = os.path.splitext(os.path.basename(video_path))[0]
    video_output_folder = os.path.join(output_folder, video_name)
    os.makedirs(video_output_folder, exist_ok=True)

    total_frames = get_total_frames(video_path)
    if not total_frames:
        print(f"⚠️ Error al obtener metadata: {video_path}")
        return

    sampling_rate = 30  # 1 frame cada 0.5 segundos (60fps * 0.5)

    # Configurar comando FFmpeg
    output_template = os.path.join(video_output_folder, "frame_%06d.jpg")
    cmd = [
        'ffmpeg',
        '-i', video_path,
        '-vf', f'select=not(mod(n\\,{sampling_rate}))',  # Filtro de selección
        '-vsync', 'vfr',  # Variable frame rate
        '-qscale:v', '2',  # Calidad JPEG
        '-loglevel', 'error',
        '-stats',  # Muestra estadísticas básicas
        '-start_number', '0',  # Iniciar numeración desde 0
        output_template
    ]

    with tqdm(
        total=total_frames,
        desc=f"FFmpeg {video_name[:15]}",
        unit="frame",
        position=position,
        leave=False
    ) as pbar:
        try:
            process = subprocess.Popen(
                cmd,
                stderr=subprocess.PIPE,
                universal_newlines=True
            )
            
            # Leer salida de progreso
            while True:
                line = process.stderr.readline()
                if not line and process.poll() is not None:
                    break
                if 'frame=' in line:
                    current_frame = int(line.split('frame=')[1].split()[0])
                    pbar.n = min(current_frame, total_frames)
                    pbar.refresh()

            if process.returncode == 0:
                frame_count = len(glob.glob(os.path.join(video_output_folder, 'frame_*.jpg')))
                print(f"✅ {video_name[:15]} ({frame_count} frames)")
        except Exception as e:
            print(f"❌ Error en {video_name}: {str(e)}")

if __name__ == "__main__":
    current_dir = os.path.dirname(os.path.abspath(__file__))
    two_folders_up = os.path.abspath(os.path.join(current_dir, "../../"))
    video_dir = os.path.join(two_folders_up, "Videos")

    if not os.path.exists(video_dir):
        raise FileNotFoundError(f"⚠️ Carpeta no encontrada: {video_dir}")

    output_folder = os.path.join(current_dir, "frames")
    os.makedirs(output_folder, exist_ok=True)

    video_files = glob.glob(os.path.join(video_dir, "*.mp4"))
    if not video_files:
        print("⚠️ No hay videos MP4")
        exit()

    # Usar threads para mantener paralelismo
    threads = []
    for idx, video in enumerate(video_files):
        t = threading.Thread(
            target=process_video,
            args=(video, output_folder, idx)
        )
        threads.append(t)
        t.start()

    for t in threads:
        t.join()

    print("\n✅ Extracción completa!")