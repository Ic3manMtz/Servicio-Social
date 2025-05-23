import subprocess
import sys
import os
import importlib.util

def check_package_installed(package_name):
    """Verifica si un paquete está instalado"""
    spec = importlib.util.find_spec(package_name)
    return spec is not None

def install_packages():
    # Lista de paquetes a instalar con sus respectivos comandos pip
    packages = [
        ["torch", "torchvision", "opencv-python", "numpy", "pandas", "scikit-learn", "matplotlib", "seaborn"],
        ["ultralytics"],
        ["deep-sort-realtime"],
        ["ffmpeg-python"]
    ]

    # Aplanar la lista de paquetes para verificación
    all_packages = [pkg for group in packages for pkg in group]
    
    # Verificar paquetes ya instalados
    installed = []
    missing = []
    
    for pkg in all_packages:
        if check_package_installed(pkg):
            installed.append(pkg)
        else:
            missing.append(pkg)
    
    # Mostrar estado de los paquetes
    if installed:
        print("✅ Paquetes ya instalados:")
        print(", ".join(installed))
        print()
    
    if not missing:
        print("✅ Todos los paquetes requeridos ya están instalados!")
        return
    
    print("🔍 Paquetes faltantes:")
    print(", ".join(missing))
    print("\nInstalando paquetes faltantes...\n")
    
    # Instalar solo los grupos que contengan paquetes faltantes
    for package_group in packages:
        # Filtrar solo los paquetes faltantes en este grupo
        to_install = [pkg for pkg in package_group if pkg in missing]
        
        if not to_install:
            continue
            
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", *to_install])
            print(f"✓ Paquetes instalados exitosamente: {', '.join(to_install)}")
        except subprocess.CalledProcessError as e:
            print(f"✗ Error al instalar los paquetes {to_install}: {e}")

if __name__ == "__main__":
    install_packages()
    os.system('cls' if os.name == 'nt' else 'clear')
    print("\n✅ Proceso completado!")