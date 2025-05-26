from time import sleep


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
            print("\n\tAntes de comenzar se configurará el entorno para el correcto funcionamiento")
            print("\tdel programa. Por favor, espere un momento...")
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
            options[2] = (options[2][0], f"{options[2][1]}   (Videos convertidos encontrados: {converted_count})")
        
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