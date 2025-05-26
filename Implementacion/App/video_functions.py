import subprocess
import os

class VideoFunctions:
    def __init__(self):
        self.video_folder = "/home/jorge-mtz/Documentos/Servicio-Social/Videos"
        self.output_folder = os.getcwd()
        self.environment_configured = False
    
    def configure_environment(self):
        """Configura el entorno necesario"""
        print("\nConfigurando el entorno...")
        subprocess.run([
            "python", "configuration.py"
        ])
        self.environment_configured = True
    
    def set_video_folder(self, path):
        """Establece la carpeta de videos si existe"""
        if os.path.exists(path):
            self.video_folder = path
            return True
        return False
    
    def set_output_folder(self, path):
        """Establece la carpeta de salida si existe"""
        if path and os.path.exists(path):
            self.output_folder = path
            return True
        elif not path:
            return True  # Usará el valor por defecto
        return False
    
    def process_video(self):
        """Procesa el video convirtiéndolo a frames"""
        print("\nProcesando video...")
        subprocess.run([
            "python", 
            "video_to_frames_C.py", 
            "--video_dir", self.video_folder, 
            "--output_folder", self.output_folder
        ])
    
    def count_converted_directories(self):
        """Cuenta los directorios de frames convertidos"""
        frames_path = os.path.join(self.output_folder, "frames")
        count = 0
        if os.path.exists(frames_path):
            for _, dirs, _ in os.walk(frames_path):
                count += len(dirs)
        return count
    
    def validate_paths(self):
        """Verifica que las rutas necesarias estén configuradas"""
        return self.video_folder is not None and self.output_folder is not None
    
    def detect_and_track_objects(self, directories_selected):
        """Llama al script de detección y seguimiento de objetos"""
        if not self.validate_paths():
            print("Por favor, configure las rutas antes de continuar.")
            return
        print("\nIniciando detección y seguimiento de objetos...")
        subprocess.run([
            "python", 
            "detection_tracking.py", 
            "--input_dir", self.output_folder+"/frames", 
            "--folders", *directories_selected,
            "--output_folder", self.output_folder
        ])
    
