import pandas as pd
import numpy as np
from sklearn.cluster import DBSCAN

#Aplica DBSCAN a los resultados del tracking para identificar grupos por frame.

# Cargar datos del tracking
df = pd.read_csv("tracking_results.csv")

# Parámetros de DBSCAN
eps_pixels = 50  # Ajustar según la resolución de tus frames
min_samples = 2   # Mínimo de personas para formar grupo

# Procesar cada frame
grouped = df.groupby(["video", "frame"])
results = []

for (video, frame), group in grouped:
    coordinates = group[["x1", "y1"]].values
    clustering = DBSCAN(eps=eps_pixels, min_samples=min_samples).fit(coordinates)
    group["group_id"] = clustering.labels_
    results.append(group)

# Guardar resultados con grupos
df_with_groups = pd.concat(results)
df_with_groups.to_csv("tracking_with_groups.csv", index=False)
print("Clustering completado. Resultados guardados en: tracking_with_groups.csv")