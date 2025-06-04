import subprocess

class VideoFunctions:

    @staticmethod
    def convert_video_to_frames(video_folder: str, output_folder: str) -> None:
        print("\nProcesando video...")
        subprocess.run([
            "python",
            "video_to_frames_C.py",
            "--video_dir", video_folder,
            "--output_folder", output_folder
        ])

