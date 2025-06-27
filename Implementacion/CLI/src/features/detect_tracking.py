import os
import cv2
import gc
import argparse
from ultralytics import YOLO
import concurrent.futures
from sqlalchemy.orm import scoped_session
from sqlalchemy.exc import IntegrityError
import torch

from src.database.connection import SessionLocal
from src.database.models import FrameObjectDetection, VideoMetadata

# Configuración global del modelo (se carga una sola vez)
MODEL = None

def initialize_model():
    """Inicializa el modelo YOLO una sola vez"""
    global MODEL
    if MODEL is None:
        MODEL = YOLO("yolo11n.pt")
        MODEL.verbose = False
        # Configurar dispositivo (GPU si está disponible)
        MODEL.to('cuda' if torch.cuda.is_available() else 'cpu')
    return MODEL

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
        # Usar modelo global
        model = initialize_model()

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

            # DETECCIÓN Y SEGUIMIENTO MEJORADO (como en el segundo script)
            results = model.track(
                frame,
                persist=True,
                tracker="bytetrack.yaml",
                classes=[0],  # Solo personas (ID 0 en COCO)
                verbose=False
            )
            
            # Liberar memoria inmediatamente
            del frame
            gc.collect()

            # Procesar resultados si hay detecciones
            if results[0].boxes.id is not None:
                track_ids = results[0].boxes.id.cpu().numpy().astype(int)
                boxes_xyxy = results[0].boxes.xyxy.cpu().numpy()
                
                for track_id, box in zip(track_ids, boxes_xyxy):
                    x1, y1, x2, y2 = map(float, box[:4])
                    
                    detections_batch.append(FrameObjectDetection(
                        video_id=video.video_id,
                        frame_number=frame_num,
                        track_id=int(track_id),
                        x1=x1,
                        y1=y1,
                        x2=x2,
                        y2=y2
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

# Las funciones process_batch y main permanecen iguales (sin cambios)

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

def main(input_base_dir, folders, device='cpu'):
    try:
        print("Iniciando procesamiento...")
        
        # Determinar batch_size dinámico según el dispositivo
        if device.lower() == 'cuda':
            safety_margin = 0.15  # Margen de seguridad del 10%
            # Tamaño mayor para GPU
            total_mem = torch.cuda.get_device_properties(device).total_memory
            allocated_mem = torch.cuda.memory_allocated(device)
            reserved_mem = torch.cuda.memory_reserved(device)
            
            free_mem = total_mem - (allocated_mem + reserved_mem)

            # Calcular memoria disponible con margen de seguridad
            available_mem = free_mem * (1 - safety_margin)
            
            # Estimar memoria requerida por elemento (ajustar según tu caso)
            # Esto deberías calibrarlo con tu carga de trabajo real
            mem_per_item = 440 * 1024 * 1024  # Convertir a bytes (440 MB por imagen)

            # Calcular batch size máximo
            batch_size = int(available_mem // mem_per_item)
        else:
            # Tamaño conservador para CPU
            batch_size = 2
            
        print(f"Usando batch_size = {batch_size} para dispositivo: {device}")

        # Procesar en batches dinámicos
        for i in range(0, len(folders), batch_size):
            batch = folders[i:i + batch_size]
            print(f"Procesando batch {i // batch_size + 1}: {', '.join(batch)}")
            process_batch(batch, input_base_dir)

            # Limpieza entre batches
            gc.collect()

        print("Procesamiento completado exitosamente")

    except Exception as e:
        print(f"Error durante el procesamiento: {str(e)}")
    finally:
        # Limpiar modelos globales al finalizar
        global MODEL
        if MODEL is not None:
            del MODEL
        gc.collect()

if __name__ == "__main__":
    # Verificar si hay GPU disponible
    try:
        import torch
        print(f"GPU disponible: {torch.cuda.is_available()}")
        device = 'cuda' if torch.cuda.is_available() else 'cpu'
    except ImportError:
        print("PyTorch no está instalado, usando CPU")

    parser = argparse.ArgumentParser(description="Detección y seguimiento en frames.")
    parser.add_argument("--input_dir", type=str, required=True,
                        help="Directorio base con subcarpetas de frames")
    parser.add_argument("--folders", nargs='+', required=True,
                        help="Lista de nombres de carpetas a analizar")
    args = parser.parse_args()

    main(args.input_dir, args.folders,device=device)