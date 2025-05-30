import os
import cv2
import gc
import argparse
from ultralytics import YOLO
from deep_sort_realtime.deepsort_tracker import DeepSort
import concurrent.futures
from sqlalchemy.orm import scoped_session
from sqlalchemy.exc import IntegrityError

from App.database.database import SessionLocal
from App.database.models import FrameObjectDetection, VideoMetadata

# Configuración global del modelo (se carga una sola vez)
MODEL = None
TRACKER = None

def initialize_models():
    """Inicializa los modelos una sola vez"""
    global MODEL, TRACKER
    if MODEL is None:
        MODEL = YOLO("yolov8n.pt")
        MODEL.verbose = False
        # Configurar dispositivo (GPU si está disponible)
        MODEL.to('cuda' if torch.cuda.is_available() else 'cpu')
    if TRACKER is None:
        TRACKER = DeepSort(max_age=30)
    return MODEL, TRACKER

def get_or_create_video(session, video_name):
    """Obtiene o crea un registro de video en la base de datos"""
    video = session.query(VideoMetadata).filter_by(title=video_name).first()
    if not video:
        video = VideoMetadata(title=video_name, duration=0, size=0)
        session.add(video)
        try:
            session.commit()
        except IntegrityError:
            session.rollback()
            video = session.query(VideoMetadata).filter_by(title=video_name).first()
    return video

def process_video(video_dir, input_base_dir):
    try:
        # Usar modelos globales
        model, tracker = initialize_models()
        
        frame_dir = os.path.join(input_base_dir, video_dir)
        if not os.path.isdir(frame_dir):
            return None

        frames = sorted([f for f in os.listdir(frame_dir) if f.endswith(".jpg")])
        if not frames:
            return None
        
        # Usar scoped_session para mejor manejo de conexiones
        db = scoped_session(SessionLocal)
        video = get_or_create_video(db, video_dir)
        
        # Procesar en lotes para reducir commits a la base de datos
        BATCH_SIZE = 50
        detections_batch = []
        
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

            # Procesamiento con YOLO
            results = model(frame, classes=[0], conf=0.5)
            detections = []
            for box in results[0].boxes:
                x1, y1, x2, y2 = map(int, box.xyxy[0])
                conf = float(box.conf[0])
                detections.append(([x1, y1, x2 - x1, y2 - y1], conf, "person"))

            # Seguimiento con DeepSort
            tracks = tracker.update_tracks(detections, frame=frame)
            
            # Liberar memoria inmediatamente
            del frame
            del results
            gc.collect()

            # Acumular detecciones para batch commit
            for track in tracks:
                if not track.is_confirmed():
                    continue
                
                track_id = track.track_id
                x1, y1, x2, y2 = track.to_ltrb()
                
                detections_batch.append(FrameObjectDetection(
                    video_id=video.video_id,
                    frame_number=frame_num,
                    track_id=track_id,
                    x1=float(x1),
                    y1=float(y1),
                    x2=float(x2),
                    y2=float(y2)
                ))

            # Commit por lotes
            if len(detections_batch) >= BATCH_SIZE:
                try:
                    db.bulk_save_objects(detections_batch)
                    db.commit()
                    detections_batch = []
                except Exception as e:
                    db.rollback()
                    print(f"Error en batch commit para {video_dir}: {str(e)}")
        
        # Commit final para las detecciones restantes
        if detections_batch:
            try:
                db.bulk_save_objects(detections_batch)
                db.commit()
            except Exception as e:
                db.rollback()
                print(f"Error en commit final para {video_dir}: {str(e)}")
        
        return True

    except Exception as e:
        print(f"Error procesando video {video_dir}: {str(e)}")
        return None
    finally:
        if 'db' in locals():
            db.remove()
        gc.collect()

def process_batch(video_dirs, input_base_dir):
    """Procesa un batch de videos con gestión de recursos"""
    # Reducir el número de workers según capacidad del hardware
    MAX_WORKERS = min(2, os.cpu_count() // 2)  # Usar la mitad de los cores disponibles
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        futures = {executor.submit(process_video, video_dir, input_base_dir): video_dir 
                  for video_dir in video_dirs}
        
        for future in concurrent.futures.as_completed(futures):
            video_dir = futures[future]
            try:
                result = future.result()
                if result:
                    print(f"Procesamiento completado para: {video_dir}")
            except Exception as e:
                print(f"Error procesando {video_dir}: {str(e)}")
            finally:
                # Limpieza periódica
                gc.collect()

def main(input_base_dir, folders):
    try:
        print("Iniciando procesamiento...")
        
        # Procesar en batches más pequeños
        batch_size = 2  # Reducir el tamaño del batch
        for i in range(0, len(folders), batch_size):
            batch = folders[i:i + batch_size]
            print(f"Procesando batch {i//batch_size + 1}: {', '.join(batch)}")
            process_batch(batch, input_base_dir)
            
            # Limpieza entre batches
            gc.collect()

        print("Procesamiento completado exitosamente")

    except Exception as e:
        print(f"Error durante el procesamiento: {str(e)}")
    finally:
        # Limpiar modelos globales al finalizar
        global MODEL, TRACKER
        if MODEL is not None:
            del MODEL
        if TRACKER is not None:
            del TRACKER
        gc.collect()

if __name__ == "__main__":
    # Verificar si hay GPU disponible
    try:
        import torch
        print(f"GPU disponible: {torch.cuda.is_available()}")
    except ImportError:
        print("PyTorch no está instalado, usando CPU")
    
    parser = argparse.ArgumentParser(description="Detección y seguimiento en frames.")
    parser.add_argument("--input_dir", type=str, required=True, 
                       help="Directorio base con subcarpetas de frames")
    parser.add_argument("--folders", nargs='+', required=True, 
                       help="Lista de nombres de carpetas a analizar")
    args = parser.parse_args()

    main(args.input_dir, args.folders)