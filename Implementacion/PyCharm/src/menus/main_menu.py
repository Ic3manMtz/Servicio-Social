from time import sleep
from typing import List, Tuple, Optional


class MainMenu:
    # Definimos las opciones como variables de clase estáticas
    MAIN_OPTIONS: List[Tuple[str, str]] = [
        ("1", "Seleccionar carpeta de videos"),
        ("2", "Seleccionar carpeta de salida"),
        ("3", "Pipeline de análisis de videos"),
        ("4", "Salir")
    ]

    PIPELINE_OPTIONS: List[Tuple[str, str]] = [
        ("1", "Convertir videos a frames"),
        ("2", "Detección de objetos y seguimiento"),
        ("3", "Clusterización de imágenes"),
        ("4", "Estadísticas de imágenes"),
        ("5", "Visualización de resultados"),
        ("6", "Visualización de videos con boxes"),
        ("7", "Volver al menú principal")
    ]

    @staticmethod
    def display_welcome() -> bool:
        """Muestra el mensaje de bienvenida y pregunta por la configuración"""
        print("\n" + "=" * 46)
        print(" " * 5 + "BIENVENIDO AL ANALIZADOR DE VIDEOS".center(20))
        print("=" * 46 + "\n")

        respuesta = input("¿Desea ejecutar la configuración del entorno antes de comenzar? (s/n): ").lower()
        if respuesta == 's':
            print("\n\tAntes de comenzar se configurará el entorno")
            print("\n\tpara el correcto funcionamiento del programa.")
            print("\n\tPor favor, espere un momento...")
            sleep(1)
            return True

        print("\n\tSe omitirá la configuración del entorno.")
        sleep(1)
        return False

    @staticmethod
    def display_main_menu(converted_count: Optional[int] = None) -> str:
        print("\n" + "=" * 40)
        print(" " * 10 + "ANÁLISIS DE VIDEOS".center(20))
        print("=" * 40 + "\n")

        options = MainMenu.MAIN_OPTIONS.copy()
        if converted_count is not None:
            options[2] = (options[2][0], f"{options[2][1]} (Videos convertidos: {converted_count})")

        for num, text in options:
            print(f" {num}┃ {text}")

        print("\n" + "-" * 40)
        return input(" ➤ Seleccione una opción: ")

    @staticmethod
    def display_get_folder(prompt, default=None) -> str:
        if default:
            prompt += f" (Enter para usar la ruta actual): "
        else:
            prompt += ": "
        return input(prompt)

    @staticmethod
    def display_pipeline_options():
        print("\n" + "="*40)
        print(" " * 10 + "PIPELINE DE ANÁLISIS".center(20))
        print("="*40 + "\n")

        for num, text in MainMenu.PIPELINE_OPTIONS:
            print(f" {num}┃ {text}")

        print("\n" + "-"*40)
        return input(" ➤ Seleccione una opción: ")

    @staticmethod
    def display_paths_confirmation(video_folder: str, output_folder: str) -> str:
        print(f"\nCarpeta de videos: {video_folder}")
        print(f"Carpeta de salida: {output_folder}")
        return input("¿Son correctas estas rutas? (s/n): ").lower()