import subprocess

from src.database.connection import SessionLocal
from src.database.db_crud import VideoCRUD
from src.database.models import VideoMetadata


class VideoFunctions:

    @staticmethod
    def convert_video_to_frames(video_folder: str, output_folder: str) -> None:
        print("\nProcesando video...")
        subprocess.run([
            "python",
            "features/video_to_frames_concurrent.py",
            "--video_dir", video_folder,
            "--output_folder", output_folder
        ])

    @staticmethod
    def detect_and_track(directories_selected, output_folder) -> None:
        subprocess.run([
            "python",
            "features/detect_tracking.py",
            "--input_dir", output_folder,
            "--folders", *directories_selected
        ])

    @staticmethod
    def reconstruct_video(directories_selected, output_folder) -> None:
        subprocess.run([
            "python",
            "features/reconstruct_video.py",
            "--input_dir", output_folder + "/frames",
            "--folders", *directories_selected,
            "--output_folder", output_folder
        ])

    @staticmethod
    def get_frames_analyzed() -> list[VideoMetadata]:
        session = SessionLocal()
        try:
            videoCRUD = VideoCRUD(session)
            frames_selected = videoCRUD.get_all_videos_with_detections()
            return frames_selected
        except Exception as e:
            print(f"Error al obtener frames analizados: {e}")
            session.rollback()  # Importante para revertir cambios si hay error
            return []
        finally:
            session.close()