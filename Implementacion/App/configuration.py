import subprocess
import sys
import os

def install_packages():
    # Lista de paquetes a instalar con sus respectivos comandos pip
    packages = [
        ["torch", "torchvision", "opencv-python", "numpy", "pandas", "scikit-learn", "matplotlib", "seaborn"],
        ["ultralytics"],
        ["deep-sort-realtime"],
        ["ffmpeg-python"]
    ]

    # Instalar cada grupo de paquetes
    for package_group in packages:
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", *package_group])
            print(f"Paquetes instalados exitosamente: {', '.join(package_group)}")
        except subprocess.CalledProcessError as e:
            print(f"Error al instalar los paquetes {package_group}: {e}")

if __name__ == "__main__":
    install_packages()
    os.system('cls' if os.name == 'nt' else 'clear')
    print("\n✅ Instalación completada!")