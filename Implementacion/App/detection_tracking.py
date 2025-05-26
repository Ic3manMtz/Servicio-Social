import os
import cv2
import csv
import argparse
from ultralytics import YOLO
from deep_sort_realtime.deepsort_tracker import DeepSort

# Combina detección (YOLOv8) y seguimiento (DeepSORT), guardando coordenadas y IDs en un CSV.

def main(input_base_dir, output_csv):
    # Configuración
    model = YOLO("yolov8n.pt")
    tracker = DeepSort(max_age=30)

    # Inicializar CSV
    with open(output_csv, mode='w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(["video", "frame", "track_id", "x1", "y1", "x2", "y2"])

    # Procesar cada video
    for video_dir in os.listdir(input_base_dir):
        frame_dir = os.path.join(input_base_dir, video_dir)
        if not os.path.isdir(frame_dir):
            continue

        frames = sorted([f for f in os.listdir(frame_dir) if f.endswith(".jpg")])
        for frame_name in frames:
            frame_path = os.path.join(frame_dir, frame_name)
            frame = cv2.imread(frame_path)
            frame_num = int(frame_name.split("_")[1].split(".")[0])

            # Detección con YOLO
            results = model(frame, classes=[0], conf=0.5)
            detections = []
            for box in results[0].boxes:
                x1, y1, x2, y2 = map(int, box.xyxy[0])
                conf = float(box.conf[0])
                detections.append(([x1, y1, x2 - x1, y2 - y1], conf, "person"))

            # Seguimiento con DeepSORT
            tracks = tracker.update_tracks(detections, frame=frame)

            # Guardar resultados en CSV
            with open(output_csv, mode='a', newline='') as f:
                writer = csv.writer(f)
                for track in tracks:
                    if not track.is_confirmed():
                        continue
                    track_id = track.track_id
                    x1, y1, x2, y2 = track.to_ltrb()
                    writer.writerow([video_dir, frame_num, track_id, x1, y1, x2, y2])

    print("Tracking completado. Resultados guardados en:", output_csv)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Detección y seguimiento en frames.")
    parser.add_argument("--input_dir", type=str, required=True, help="Directorio base con subcarpetas de frames")
    parser.add_argument("--output_folder", type=str, default="tracking_results.csv", help="Archivo CSV de salida")
    args = parser.parse_args()

    # main(args.input_dir, args.output_csv)