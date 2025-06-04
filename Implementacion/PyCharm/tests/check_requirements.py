import subprocess
import sys
import platform
import importlib.util
from pathlib import Path


def check_python_version():
    req_version = (3, 10)
    cur_version = sys.version_info
    if cur_version < req_version:
        raise RuntimeError(f"Se requiere Python 3.10+ (actual: {platform.python_version()}")


def check_os():
    system = platform.system().lower()
    if system not in ['linux', 'darwin', 'windows']:
        print(f"Advertencia: Sistema operativo no probado: {system}")


def load_requirements():
    script_dir = Path(__file__).parent  # Directorio tests/
    project_root = script_dir.parent  # Directorio raíz del proyecto

    file_path = project_root / 'requirements.txt'
    requirements = []
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            for line in file:
                line = line.strip()
                # Ignora comentarios y líneas vacías
                if line and not line.startswith('#'):
                    # Elimina especificaciones de versión (todo lo después del primer caracter no alfanumérico)
                    package = line.split('[')[0].split('<')[0].split('>')[0].split('=')[0].split('~')[0].strip()
                    if package:
                        requirements.append(package)
    except FileNotFoundError:
        print(f"⚠ Advertencia: No se encontró el archivo {file_path}")
    return requirements


def check_dependencies(requirements):
    """Verifica si los paquetes requeridos están instalados"""
    if not requirements:
        print("No se encontraron dependencias para verificar")
        return True

    print("\nVerificando dependencias:")
    missing_deps = []

    for package in requirements:
        spec = importlib.util.find_spec(package)
        if spec is None:
            # Intenta con nombres alternativos comunes
            alt_names = {
                'opencv-python': ['cv2'],
                'Pillow': ['PIL'],
                'scikit-learn': ['sklearn'],
                'python-dotenv': ['dotenv'],
                'psycopg2-binary': ['psycopg2']
            }

            found = False
            for alt in alt_names.get(package, []):
                if importlib.util.find_spec(alt):
                    print(f"✓ {package} (como '{alt}') está instalado")
                    found = True
                    break

            if not found:
                print(f"✗ Falta: {package}")
                missing_deps.append(package)
        else:
            print(f"✓ {package} está instalado")

    if missing_deps:
        print("\n✗ Faltan las siguientes dependencias:")
        for dep in missing_deps:
            print(f"- {dep}")
        return missing_deps

    print("\n✓ Todas las dependencias están instaladas")
    return []

def install_dependencies(missing_deps):
    # Primero actualizamos pip
    try:
        print("\n🔄 Actualizando pip...")
        subprocess.check_call([sys.executable, '-m', 'pip', 'install', '--upgrade', 'pip'])
        print("✅ pip actualizado correctamente")
    except subprocess.CalledProcessError as e:
        print(f"⚠ No se pudo actualizar pip (el script puede continuar): {e}")

    # Luego instalamos las dependencias faltantes
    try:
        print("\n🔄 Instalando dependencias faltantes...")
        subprocess.check_call([sys.executable, '-m', 'pip', 'install', *missing_deps])
        print("\n✨ Dependencias instaladas correctamente!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"\n❌ Error instalando dependencias: {e}")
        return False

if __name__ == "__main__":
    check_python_version()
    check_os()

    # Cargar dependencias desde requirements.txt
    requirements = load_requirements()

    # Verificar dependencias
    missing_deps = check_dependencies(requirements)

    if missing_deps==[]:
        print("\n✓ Todos los requisitos cumplidos")
        sys.exit(0)
    else:
        response=input("\n✗ Hay dependencias faltantes, desea instalarlas en este momento? (s/n):").lower()
        if response=='s':
            install_dependencies(missing_deps)
        else:
            print("\nPuedes instalarlas con:")
            print(f"pip install {' '.join(missing_deps)}")
        sys.exit(1)