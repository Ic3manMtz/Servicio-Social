import os
import cv2
import csv
import argparse
from ultralytics import YOLO
from deep_sort_realtime.deepsort_tracker import DeepSort
import concurrent.futures
from tqdm import tqdm
import warnings
from contextlib import redirect_stdout, redirect_stderr
import io

# Configuración global para silenciar advertencias
warnings.filterwarnings("ignore")

class SilentOutput:
    """Context manager para silenciar completamente la salida"""
    def __enter__(self):
        self._original_stdout = sys.stdout
        self._original_stderr = sys.stderr
        sys.stdout = io.StringIO()
        sys.stderr = io.StringIO()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        sys.stdout = self._original_stdout
        sys.stderr = self._original_stderr

def process_video(video_dir, input_base_dir, output_csv):
    try:
        # Silenciamos completamente la carga del modelo
        with SilentOutput():
            model = YOLO("yolov8n.pt")
            model.verbose = False
            tracker = DeepSort(max_age=30)
        
        frame_dir = os.path.join(input_base_dir, video_dir)
        if not os.path.isdir(frame_dir):
            return None

        frames = sorted([f for f in os.listdir(frame_dir) if f.endswith(".jpg")])
        if not frames:
            return None
        
        temp_csv = os.path.join(os.path.dirname(output_csv), f"temp_{video_dir}.csv")
        with open(temp_csv, mode='w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(["video", "frame", "track_id", "x1", "y1", "x2", "y2"])

        progress_bar = tqdm(frames, desc=f"{video_dir[:15]:<15}", leave=False, 
                          bar_format='{l_bar}{bar}| {n_fmt}/{total_fmt}')
        
        for frame_name in progress_bar:
            frame_path = os.path.join(frame_dir, frame_name)
            if not os.path.exists(frame_path):
                continue

            frame = cv2.imread(frame_path)
            if frame is None:
                continue

            try:
                frame_num = int(frame_name.split("_")[1].split(".")[0])
            except (IndexError, ValueError):
                continue

            # Silenciamos completamente la inferencia del modelo
            with SilentOutput():
                results = model(frame, classes=[0], conf=0.5, verbose=False)
                
            detections = []
            for box in results[0].boxes:
                x1, y1, x2, y2 = map(int, box.xyxy[0])
                conf = float(box.conf[0])
                detections.append(([x1, y1, x2 - x1, y2 - y1], conf, "person"))

            tracks = tracker.update_tracks(detections, frame=frame)

            with open(temp_csv, mode='a', newline='') as f:
                writer = csv.writer(f)
                for track in tracks:
                    if not track.is_confirmed():
                        continue
                    track_id = track.track_id
                    x1, y1, x2, y2 = track.to_ltrb()
                    writer.writerow([video_dir, frame_num, track_id, x1, y1, x2, y2])
        
        progress_bar.close()
        return temp_csv

    except Exception:
        return None

def main(input_base_dir, folders, output_folder):
    try:
        os.makedirs(os.path.join(output_folder, "results"), exist_ok=True)
        output_csv = os.path.join(output_folder, "results", "tracking_results.csv")
        
        with open(output_csv, mode='w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(["video", "frame", "track_id", "x1", "y1", "x2", "y2"])

        main_progress = tqdm(total=len(folders), desc="Progreso general", 
                           bar_format='{l_bar}{bar}| {n_fmt}/{total_fmt} [carpetas]')
        
        with concurrent.futures.ThreadPoolExecutor() as executor:
            futures = []
            for video_dir in folders:
                future = executor.submit(process_video, video_dir, input_base_dir, output_csv)
                futures.append(future)
            
            for future in concurrent.futures.as_completed(futures):
                temp_csv = future.result()
                if temp_csv and os.path.exists(temp_csv):
                    try:
                        with open(temp_csv, mode='r') as temp_f, open(output_csv, mode='a', newline='') as main_f:
                            reader = csv.reader(temp_f)
                            next(reader)
                            writer = csv.writer(main_f)
                            for row in reader:
                                writer.writerow(row)
                        os.remove(temp_csv)
                    except Exception:
                        pass
                main_progress.update(1)

        main_progress.close()
        print("\nProcesamiento completado")

    except Exception:
        pass

if __name__ == "__main__":
    import sys  # Necesario para SilentOutput
    
    parser = argparse.ArgumentParser(description="Detección y seguimiento en frames.")
    parser.add_argument("--input_dir", type=str, required=True, 
                       help="Directorio base con subcarpetas de frames")
    parser.add_argument("--folders", nargs='+', required=True, 
                       help="Lista de nombres de carpetas a analizar")
    parser.add_argument("--output_folder", type=str, required=True,
                       help="Directorio base donde se creará la carpeta 'results'")
    args = parser.parse_args()

    main(args.input_dir, args.folders, args.output_folder)