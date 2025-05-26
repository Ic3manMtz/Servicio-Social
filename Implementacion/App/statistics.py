import pandas as pd
import matplotlib.pyplot as plt

# Calcula métricas estadísticas de los grupos.

df = pd.read_csv("tracking_with_groups.csv")

# 1. Tamaño promedio de grupos por video
group_sizes = df[df["group_id"] != -1].groupby(["video", "frame", "group_id"]).size().reset_index(name="size")
avg_group_size = group_sizes.groupby("video")["size"].mean()
print("Tamaño promedio de grupos por video:\n", avg_group_size)

# 2. Distribución de tamaños de grupos
plt.hist(group_sizes["size"], bins=range(1, 10))
plt.xlabel("Tamaño del grupo")
plt.ylabel("Frecuencia")
plt.title("Distribución de tamaños de grupos")
plt.savefig("group_size_distribution.png")
plt.close()

# 3. Estabilidad temporal (ejemplo: % de frames donde un track_id está en el mismo grupo)
# (Requiere análisis más avanzado por simplicidad)