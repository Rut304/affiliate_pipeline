import subprocess
from pathlib import Path

def merge_with_audio(video_path, audio_path="narration.mp3"):
    video_path = Path(video_path)
    audio_path = Path(audio_path)
    out_path = video_path.with_name(f"{video_path.stem}_with_audio.mp4")

    subprocess.run([
        "ffmpeg", "-y",
        "-i", str(video_path),
        "-i", str(audio_path),
        "-c:v", "copy",
        "-c:a", "aac",
        "-shortest",
        str(out_path)
    ], check=True)

    print(f"[OK] Merged: {out_path}")
    return out_path

if __name__ == "__main__":
    # 🔹 EXAMPLE USAGE:
    # For a single video
    merge_with_audio("Segmind Video - No Sound.mp4", "narration.mp3")

    # For a whole folder (all MP4s without audio)
    # Path("outputs").glob("*No Sound.mp4")
    # for vid in Path("outputs").glob("*No Sound.mp4"):
    #     merge_with_audio(vid)
