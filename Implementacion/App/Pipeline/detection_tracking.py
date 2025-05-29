import os
import cv2
import argparse
from ultralytics import YOLO
from deep_sort_realtime.deepsort_tracker import DeepSort
import concurrent.futures
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import IntegrityError

from App.database.database import SessionLocal, engine
from App.database.models import FrameObjectDetection, VideoMetadata


# Configuración de la base de datos
Session = sessionmaker(bind=engine)

def get_or_create_video(session, video_name):
    """Obtiene o crea un registro de video en la base de datos"""
    video = session.query(VideoMetadata).filter_by(title=video_name).first()
    if not video:
        video = VideoMetadata(title=video_name, duration=0, size=0)  # Valores dummy, puedes ajustarlos
        session.add(video)
        try:
            session.commit()
        except IntegrityError:
            session.rollback()
            video = session.query(VideoMetadata).filter_by(title=video_name).first()
    return video

def process_video(video_dir, input_base_dir):
    try:
        model = YOLO("yolov8n.pt")
        model.verbose = False
        tracker = DeepSort(max_age=30)
        
        frame_dir = os.path.join(input_base_dir, video_dir)
        if not os.path.isdir(frame_dir):
            return None

        frames = sorted([f for f in os.listdir(frame_dir) if f.endswith(".jpg")])
        if not frames:
            return None
        
        # Crear una sesión de base de datos por hilo
        db = SessionLocal()
        video = get_or_create_video(db, video_dir)
        
        for frame_name in frames:
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

            results = model(frame, classes=[0], conf=0.5)
            detections = []
            for box in results[0].boxes:
                x1, y1, x2, y2 = map(int, box.xyxy[0])
                conf = float(box.conf[0])
                detections.append(([x1, y1, x2 - x1, y2 - y1], conf, "person"))

            tracks = tracker.update_tracks(detections, frame=frame)

            for track in tracks:
                if not track.is_confirmed():
                    continue
                
                track_id = track.track_id
                x1, y1, x2, y2 = track.to_ltrb()
                
                # Crear registro en la base de datos
                detection = FrameObjectDetection(
                    video_id=video.video_id,
                    frame_number=frame_num,
                    track_id=track_id,
                    x1=float(x1),
                    y1=float(y1),
                    x2=float(x2),
                    y2=float(y2)
                )
                
                db.add(detection)
            
            # Commit por cada frame para no perder datos si hay error
            try:
                db.commit()
            except Exception as e:
                db.rollback()
                print(f"Error al guardar frame {frame_num} de {video_dir}: {str(e)}")
        
        db.close()
        return True

    except Exception as e:
        print(f"Error procesando video {video_dir}: {str(e)}")
        return None
    finally:
        if 'db' in locals():
            db.close()

def process_batch(video_dirs, input_base_dir):
    """Procesa un batch de videos con un máximo de 6 hilos"""
    with concurrent.futures.ThreadPoolExecutor(max_workers=6) as executor:
        futures = {executor.submit(process_video, video_dir, input_base_dir): video_dir for video_dir in video_dirs}
        
        for future in concurrent.futures.as_completed(futures):
            video_dir = futures[future]
            try:
                result = future.result()
                if result:
                    print(f"Procesamiento completado para: {video_dir}")
            except Exception as e:
                print(f"Error procesando {video_dir}: {str(e)}")

def main(input_base_dir, folders, output_folder):
    try:
        print("Iniciando procesamiento...")
        
        os.makedirs(os.path.join(output_folder, "results"), exist_ok=True)
        
        # Procesar en batches de máximo 6 videos a la vez para un CPU con seis núcleos
        batch_size = 6
        for i in range(0, len(folders), batch_size):
            batch = folders[i:i + batch_size]
            print(f"Procesando batch {i//batch_size + 1}: {', '.join(batch)}")
            process_batch(batch, input_base_dir)

        print("Procesamiento completado exitosamente")

    except Exception as e:
        print(f"Error durante el procesamiento: {str(e)}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Detección y seguimiento en frames.")
    parser.add_argument("--input_dir", type=str, required=True, 
                       help="Directorio base con subcarpetas de frames")
    parser.add_argument("--folders", nargs='+', required=True, 
                       help="Lista de nombres de carpetas a analizar")
    parser.add_argument("--output_folder", type=str, required=True,
                       help="Directorio base donde se creará la carpeta 'results'")
    args = parser.parse_args()

    main(args.input_dir, args.folders, args.output_folder)