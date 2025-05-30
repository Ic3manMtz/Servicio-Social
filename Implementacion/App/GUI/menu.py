from time import sleep
import os

class Menu:
    def __init__(self):
        self.options = [
            ("1", "Seleccionar carpeta de videos"),
            ("2", "Seleccionar carpeta de salida"),
            ("3", "Convertir videos a frames"),
            ("4", "Pipeline de análisis de videos"),
            ("5", "Salir")
        ]
        self.pipeline_optiones = [
            ("1", "Detección de objetos y seguimiento"),
            ("2", "Clusterización de imágenes"),
            ("3", "Estadísticas de imágenes"),
            ("4", "Viusualización de resultados"),
            ("5", "Relizar análisis completo"),
            ("6", "Volver al menú principal")
        ]

    def display_welcome(self):
        """Muestra el mensaje de bienvenida"""
        print("\n" + "="*46)
        print(" " * 5 + "BIENVENIDO AL ANALIZADOR DE VIDEOS".center(20))
        print("="*46 + "\n")
        respuesta = input("¿Desea ejecutar la configuración del entorno antes de comenzar? (s/n): ").lower()
        if respuesta == 's':
            print("\n\tAntes de comenzar se configurará el entorno ")
            print("\n\tpara el correcto funcionamiento del programa. ")
            print("\n\tPor favor, espere un momento...")
            sleep(1)
            return True
        else:
            print("\n\tSe omitirá la configuración del entorno.")
            sleep(1)
            return False
    
    def display_main_menu(self, converted_count=None):
        """Muestra el menú principal con las opciones disponibles"""
        print("\n" + "="*40)
        print(" " * 10 + "ANÁLISIS DE VIDEOS".center(20))
        print("="*40 + "\n")
        
        # Actualizar la opción 4 con el contador si está disponible
        options = self.options.copy()
        if converted_count is not None:
            options[2] = (options[2][0], f"{options[2][1]} (Videos convertidos encontrados: {converted_count})")
        
        for num, text in options:
            print(f" {num}┃ {text}")
        
        print("\n" + "-"*40)
        return input(" ➤ Seleccione una opción: ")
    
    def display_confirmation(self, video_folder, output_folder):
        """Muestra confirmación de rutas"""
        print(f"\nCarpeta de videos: {video_folder}")
        print(f"Carpeta de salida: {output_folder}")
        return input("¿Son correctas estas rutas? (s/n): ").lower()
    
    def get_folder_input(self, prompt, default=None):
        """Obtiene entrada de carpeta del usuario"""
        if default:
            prompt += f" (Enter para usar la ruta actual): "
        else:
            prompt += ": "
        return input(prompt)
    
    def display_pipeline_selection(self):
        """Muestra la selección del pipeline de análisis"""
        print("\n" + "="*40)
        print(" " * 10 + "PIPELINE DE ANÁLISIS".center(20))
        print("="*40 + "\n")

        for num, text in self.pipeline_optiones:
            print(f" {num}┃ {text}")

        print("\n" + "-"*40)
        return input(" ➤ Seleccione una opción: ")
    
    def display_frame_folders(self, frames_path):
        """Muestra las carpetas de frames convertidos"""
        print("\n" + "="*40)
        print(" " * 5 + "CARPETAS DE FRAMES CONVERTIDOS".center(20))
        print("="*40 + "\n")
        
        if os.path.exists(frames_path):
            dir_names = []
            for _, dirs, _ in os.walk(frames_path):
                dir_names = dirs
                break  # Solo queremos el primer nivel de carpetas

            if not dir_names:
                print("No se encontraron carpetas de frames.")
                return []

            print("Seleccione las carpetas que desea usar (separe los números con comas):")
            for idx, dir_name in enumerate(dir_names, 1):
                print(f"  {idx}. {dir_name}")

            seleccion = input("\nIngrese los números de las carpetas, separados por comas (Enter para seleccionar todas): ").strip()
            if not seleccion:
                # Si el usuario presiona Enter, selecciona todas las carpetas
                seleccionados = dir_names
            else:
                indices = [int(i.strip()) for i in seleccion.split(",") if i.strip().isdigit()]
                seleccionados = [dir_names[i-1] for i in indices if 1 <= i <= len(dir_names)]
            return seleccionados
        
        print("\n" + "-"*40)
        input("Presione Enter para continuar...")