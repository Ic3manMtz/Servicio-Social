import os

from src.features.video_functions import VideoFunctions
from src.menus.main_menu import MainMenu
from tests.check_requirements import *

class Handler:
    def __init__(self):
        self.video_folder = ""
        self.output_folder = os.getcwd()

    def configure_requirements(self):
        check_python_version()
        check_os()
        requirements = load_requirements()

        missing_deps = check_dependencies(requirements)

        if missing_deps == []:
            print("\n✓ Todos los requisitos cumplidos")
        else:
            response = input("\n✗ Hay dependencias faltantes, desea instalarlas en este momento? (s/n):").lower()
            if response == 's':
                install_dependencies(missing_deps)
            else:
                print("\nPuedes instalarlas con:")
                print(f"pip install {' '.join(missing_deps)}")

    def main_menu(self, choice):
        if choice == '1':
            self.set_video_folder()
        elif choice == '2':
            self.set_output_folder()
        elif choice == '3':
            self.pipeline_options()
        elif choice == '4':
            print("Salir")
            sys.exit(1)
        else:
            print("\nOpcion invalida, intente de nuevo")

    def set_video_folder(self):
        path = MainMenu.display_get_folder("\nIngresa la ruta de la carpeta con los videos", default=None)

        if os.path.exists(path):
            self.video_folder = path
            print(f"\n\tRuta seleccionada: {self.video_folder}")
        else:
            print("La ruta especificada no existe. Inténtelo de nuevo.")

    def set_output_folder(self):
        path = MainMenu.display_get_folder("\nIngresa la ruta de la carpeta con los videos", default=1)

        if path == "":
            self.output_folder = os.getcwd()
            print(f"\n\tRuta seleccionada: {self.output_folder}")
        elif os.path.exists(path):
            self.output_folder = path
            print(f"\n\tRuta seleccionada: {self.output_folder}")
        else:
            print("La ruta especificada no existe. Inténtelo de nuevo.")

    def pipeline_options(self):
        while True:
            choice = MainMenu.display_pipeline_options()

            if choice == '1':
                response = MainMenu.display_paths_confirmation(video_folder=self.video_folder, output_folder=self.output_folder)
                if response == 's':
                    VideoFunctions.convert_video_to_frames(self.video_folder, self.output_folder)
            elif choice == '2':
                directories_selected = MainMenu.display_frame_folders(self.output_folder+"/frames")
                VideoFunctions.detect_and_track(directories_selected, self.output_folder+"/frames")
            elif choice == '3':
                print("Clusterización de imágenes")
            elif choice == '4':
                print("Estadísticas de imágenes")
            elif choice == '5':
                print("Visualización de resultados")
            elif choice == '6':
                frames_analyzed = VideoFunctions.get_frames_analyzed()
                frames_selected = MainMenu.display_frames_analysed(frames_analyzed)
                VideoFunctions.reconstruct_video(frames_selected, self.output_folder)
            elif choice == '7':
                print("Regresar al menu anterior")
                break
            else:
                print("\nOpcion invalida, intente de nuevo")
