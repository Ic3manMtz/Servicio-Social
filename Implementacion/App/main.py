import subprocess
import os

class VideoAnalyzer:
    def __init__(self):
        self.video_folder = None
        self.output_folder = os.getcwd()  # Ruta actual por defecto
        self.environment_configured = False
    
    def main_menu(self):
        while True:
            print("\n" + "="*40)
            print(" " * 10 + "ANÁLISIS DE VIDEOS".center(20))
            print("="*40 + "\n")
            
            opciones = [
                ("1", "Configuración del entorno"),
                ("2", "Seleccionar carpeta de videos"),
                ("3", "Seleccionar carpeta de salida"),
                ("4", f"Convertir videos a frames   (Viceos convertidos encontrados: {self.count_directories()})"),
                ("5", "Seleccionar modelo de análisis"),
                ("6", "Salir")
            ]
            
            for num, texto in opciones:
                print(f" {num}┃ {texto}")
            
            print("\n" + "-"*40)
            choice = input(" ➤ Seleccione una opción: ")

            if choice == "1":
                self.configure_environment()
                self.environment_configured = True
            elif choice == "2":
                self.select_video_folder()
            elif choice == "3":
                self.select_output_folder()
            elif choice == "4":
                self.validate_paths()
            elif choice == "5":
                self.model_selection()
            elif choice == "6":
                print("Saliendo del programa...")
                break
            else:
                print("Opción inválida. Intente de nuevo.")

    def configure_environment(self):    
        print("\nConfigurando el entorno...")
        subprocess.run([
            "python",
            "configuration.py"
        ])

    def select_video_folder(self):
        video_folder = input("Ingresa la ruta de la carpeta con los videos: ")
        if os.path.exists(video_folder):
            self.video_folder = video_folder
            print(f"Ruta seleccionada: {self.video_folder}")
        else:
            print("La ruta especificada no existe. Inténtelo de nuevo.")
            self.video_folder = None
    
    def select_output_folder(self):
        output_folder = input("Ingresa la ruta para guardar resultados (Enter para usar actual): ")
        if output_folder:
            if os.path.exists(output_folder):
                self.output_folder = output_folder
                print(f"Ruta de salida seleccionada: {self.output_folder}")
            else:
                print("La ruta especificada no existe. Usando ruta actual.")
        else:
            print(f"Usando ruta actual: {self.output_folder}")
    
    def validate_paths(self):
        if self.video_folder and self.output_folder:
            print(f"\nCarpeta de videos: {self.video_folder}")
            print(f"Carpeta de salida: {self.output_folder}")
            confirm = input("¿Son correctas estas rutas? (s/n): ").lower()
            if confirm == 's':
                self.process_video()
            else:
                print("Por favor, seleccione las rutas correctas.")
        else:
            print("Debe seleccionar ambas rutas antes de procesar.")
    
    def process_video(self):
        print("\nProcesando video...")
        subprocess.run([
            "python", 
            "video_to_frames_C.py", 
            "--video_dir", self.video_folder, 
            "--output_folder", self.output_folder
        ])
    
    def count_directories(self):
        frames_path = os.path.join(self.output_folder, "frames")
        count = 0
        for _, dirs, _ in os.walk(frames_path):
            count += len(dirs)
        return count

    def model_selection(self):
        print("\nSeleccionando modelo de análisis...")
        # Aquí iría la lógica para seleccionar el modelo de análisis
        # YOLOv8x
        # 

if __name__ == "__main__":
    analyzer = VideoAnalyzer()
    analyzer.main_menu()