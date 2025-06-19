import cv2
import os
import torch
from ultralytics import YOLO

def process_frames(frames_folder, model_path="yolo11n.pt"):
    # Cargar el modelo YOLO
    model = YOLO(model_path).to('cuda' if torch.cuda.is_available() else 'cpu')
    
    # Obtener lista ordenada de frames
    frame_files = sorted([
        f for f in os.listdir(frames_folder) 
        if f.lower().endswith(('.jpg', '.png', '.jpeg', '.bmp'))
    ])
    
    if not frame_files:
        print(f"No se encontraron imágenes en: {frames_folder}")
        return
    
    print(f"Procesando {len(frame_files)} frames...")
    
    # Procesar cada frame
    for frame_file in frame_files:
        frame_path = os.path.join(frames_folder, frame_file)
        frame = cv2.imread(frame_path)
        
        if frame is None:
            print(f"Error al leer el frame: {frame_file}")
            continue
            
        # Ejecutar detección y tracking
        results = model.track(
            frame,
            persist=True,
            tracker="bytetrack.yaml",
            classes=[0],  # Solo detectar personas (ID 0 en COCO)
            )
        
        # Visualizar resultados
        annotated_frame = results[0].plot()
        
        # Mostrar frame procesado
        cv2.imshow("YOLO Tracking", annotated_frame)
        
        # Opciones de control:
        # - 'q' para salir
        # - 'p' para pausar
        key = cv2.waitKey(25) & 0xFF
        if key == ord('q'):
            break
        elif key == ord('p'):
            cv2.waitKey(0)
    
    cv2.destroyAllWindows()
    print("Procesamiento completado")

if __name__ == "__main__":
    # Configuración
    frames_folder = "./frames/06-11-2025-V3"  # Cambiar por tu ruta
    model_path = "yolo11n.pt"  # O "yolov11n.pt" según tu modelo
    
    # Ejecutar procesamiento
    process_frames(frames_folder, model_path)