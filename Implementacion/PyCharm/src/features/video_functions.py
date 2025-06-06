import subprocess

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

