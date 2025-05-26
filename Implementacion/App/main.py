from menu import Menu
from video_functions import VideoFunctions

class Main:
    def __init__(self):
        self.menu = Menu()
        self.video_functions = VideoFunctions()
    
    def run(self):
        """Inicia el programa y muestra el menú principal"""
        if(self.menu.display_welcome()):
            self.handle_environment_config()
        """Método principal que ejecuta el programa"""
        while True:
            # Obtener conteo de directorios para mostrar en el menú
            converted_count = self.video_functions.count_converted_directories()
            
            # Mostrar menú y obtener selección
            choice = self.menu.display_main_menu(converted_count)
            
            # Manejar selección del usuario
            if choice == "1":
                self.handle_video_folder_selection()
            elif choice == "2":
                self.handle_output_folder_selection()
            elif choice == "3":
                self.handle_video_convertion()
            elif choice == "4":
                self.handle_pipeline()
            elif choice == "5":
                print("Saliendo del programa...")
                break
            else:
                print("Opción inválida. Intente de nuevo.")
    
    def handle_environment_config(self):
        """Maneja la configuración del entorno"""
        if self.video_functions.environment_configured:
            print("\n\tEl entorno ya está configurado.")
            return
        self.video_functions.configure_environment()
    
    def handle_video_folder_selection(self):
        """Maneja la selección de la carpeta de videos"""
        path = self.menu.get_folder_input("\nIngresa la ruta de la carpeta con los videos")
        if self.video_functions.set_video_folder(path):
            print(f"\n\tRuta seleccionada: {self.video_functions.video_folder}")
        else:
            print("La ruta especificada no existe. Inténtelo de nuevo.")
    
    def handle_output_folder_selection(self):
        """Maneja la selección de la carpeta de salida"""
        path = self.menu.get_folder_input(
            "\nIngresa la ruta para guardar resultados", 
            self.video_functions.output_folder
        )
        if self.video_functions.set_output_folder(path):
            print(f"\n\tRuta de salida seleccionada: {self.video_functions.output_folder}")
        else:
            print("La ruta especificada no existe. Usando ruta actual.")
    
    def handle_video_convertion(self):
        """Maneja la conversión de videos a frames"""
        if not self.video_functions.validate_paths():
            print("Debe seleccionar ambas rutas antes de procesar.")
            return
        
        confirm = self.menu.display_confirmation(
            self.video_functions.video_folder,
            self.video_functions.output_folder
        )
        
        if confirm == 's':
            self.video_functions.process_video()

    def handle_pipeline(self):
        """Maneja la selección del pipeline de análisis"""

        while True:
            choice = self.menu.display_pipeline_selection()

            if choice == "1":
                print("\nDetection and tracking...")
            elif choice == "2":
                print("\nClustering...")
            elif choice == "3":
                print("\nStatistics...")
            
                
            elif choice == "6":
                print("Regresando al menú principal...")
                break
            else:
                print("Opción inválida. Regresando al menú principal.")
                

if __name__ == "__main__":
    app = Main()
    app.run()