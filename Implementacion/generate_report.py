import os
import pandas as pd
import matplotlib.pyplot as plt

data = []
detections_root = "resultados/detections/"

# Verificar si la carpeta raíz existe
if not os.path.exists(detections_root):
    raise FileNotFoundError(f"La carpeta {detections_root} no existe")

# Iterar sobre cada elemento en la carpeta de detecciones
for item in os.listdir(detections_root):
    item_path = os.path.join(detections_root, item)
    
    # Si es un directorio (carpeta de video)
    if os.path.isdir(item_path):
        video_name = item
        # Iterar sobre los archivos en la carpeta del video
        for frame_file in os.listdir(item_path):
            if frame_file.endswith(".txt"):
                txt_path = os.path.join(item_path, frame_file)
                with open(txt_path, 'r') as f:
                    num_personas = len(f.readlines())
                num_grupos = 2  # Ajustar según tu lógica de grupos
                
                data.append({
                    "video": video_name,
                    "frame": frame_file,
                    "personas": num_personas,
                    "grupos": num_grupos
                })
    
    # Si es un archivo directamente en la carpeta raíz (sin subcarpetas)
    elif item.endswith(".txt"):
        with open(os.path.join(detections_root, item), 'r') as f:
            num_personas = len(f.readlines())
        num_grupos = 2  # Ajustar según tu lógica de grupos
        
        data.append({
            "video": "general",  # Nombre por defecto si no hay subcarpetas
            "frame": item,
            "personas": num_personas,
            "grupos": num_grupos
        })

# Verificar si se recopilaron datos
if not data:
    raise ValueError("No se encontraron archivos .txt para procesar")

# Crear DataFrame
df = pd.DataFrame(data)

# Verificar las columnas del DataFrame
print("Columnas en el DataFrame:", df.columns.tolist())

# Guardar CSV
output_dir = "resultados"
os.makedirs(output_dir, exist_ok=True)
df.to_csv(os.path.join(output_dir, "estadisticas.csv"), index=False)

# Generar gráficos
plt.figure(figsize=(12, 6))

if "video" in df.columns:
    # Si hay múltiples videos
    for video_name in df["video"].unique():
        video_df = df[df["video"] == video_name]
        plt.plot(video_df["personas"], label=f"Personas ({video_name})")
        plt.plot(video_df["grupos"], label=f"Grupos ({video_name})", linestyle="--")
else:
    # Si no hay columna de video (solo datos generales)
    plt.plot(df["personas"], label="Personas")
    plt.plot(df["grupos"], label="Grupos", linestyle="--")

plt.xlabel("Frame")
plt.ylabel("Cantidad")
plt.legend()
plt.tight_layout()
plt.savefig(os.path.join(output_dir, "grafico.png"))
plt.show()