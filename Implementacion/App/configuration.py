import subprocess
import sys
import importlib.util
from time import sleep

try:
    from tqdm import tqdm
except ImportError:
    subprocess.check_call([sys.executable, "-m", "pip", "install", "tqdm"])
    from tqdm import tqdm

def check_package_installed(package_name):
    """Verifica si un paquete está instalado"""
    spec = importlib.util.find_spec(package_name)
    return spec is not None

def install_packages():
    packages = [
        ["torch", "torchvision", "opencv-python", "numpy", "pandas", "scikit-learn", "matplotlib", "seaborn"],
        ["ultralytics"],
        ["deep-sort-realtime"],
        ["ffmpeg-python"]
    ]

    all_packages = [pkg for group in packages for pkg in group]
    missing = []

    for pkg in all_packages:
        if not check_package_installed(pkg):
            missing.append(pkg)

    if not missing:
        return

    total_to_install = sum(1 for group in packages for pkg in group if pkg in missing)
    with tqdm(total=total_to_install, desc="Instalando paquetes", ncols=80) as pbar:
        for package_group in packages:
            to_install = [pkg for pkg in package_group if pkg in missing]
            if not to_install:
                continue
            try:
                subprocess.check_call([
                    sys.executable, "-m", "pip", "install", *to_install],
                    stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            except subprocess.CalledProcessError:
                pass
            pbar.update(len(to_install))

if __name__ == "__main__":
    install_packages()
    sleep(0.5)
    print("\n✅ Proceso completado!")