import cv2
import pandas as pd
import numpy as np

# Genera visualizaciones de los grupos en frames clave.

df = pd.read_csv("tracking_with_groups.csv")
video_dir = "data/video_1"  # Ejemplo para un video

# Colores para grupos
colors = np.random.randint(0, 255, (100, 3))  # Máx 100 grupos

for frame_num in df["frame"].unique()[:10]:  # Procesar primeros 10 frames
    frame_path = f"{video_dir}/frame_{frame_num:04d}.jpg"
    frame = cv2.imread(frame_path)
    frame_data = df[(df["video"] == "video_1") & (df["frame"] == frame_num)]
    
    for _, row in frame_data.iterrows():
        x1, y1, x2, y2, group_id = row[["x1", "y1", "x2", "y2", "group_id"]]
        color = colors[group_id % 100] if group_id != -1 else (0, 0, 255)  # Rojo para outliers
        cv2.rectangle(frame, (x1, y1), (x2, y2), color.tolist(), 2)
        cv2.putText(frame, f"G: {group_id}", (x1, y1 - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color.tolist(), 1)
    
    cv2.imwrite(f"output/video_1_frame_{frame_num}_groups.jpg", frame)
print("Visualizaciones guardadas en /output")