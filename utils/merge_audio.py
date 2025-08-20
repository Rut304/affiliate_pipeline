import subprocess
from pathlib import Path

def merge_with_audio(video_path, audio_path="narration.mp3"):
    """
    Merge an MP4 video with an audio track into a final MP4 with sound.

    - Handles spaces in filenames
    - Preserves video quality (no re-encode of video stream)
    - Encodes audio to AAC for MP4 compatibility
    - Trims to the shortest stream to avoid trailing silence or black frames
    """
    video_path = Path(video_path)
    audio_path = Path(audio_path)

    if not video_path.exists():
        raise FileNotFoundError(f"Video file not found: {video_path}")
    if not audio_path.exists():
        raise FileNotFoundError(f"Audio file not found: {audio_path}")

    output_path = video_path.with_name(f"{video_path.stem}_with_audio.mp4")

    subprocess.run([
        "ffmpeg", "-y",
        "-i", str(video_path),
        "-i", str(audio_path),
        "-c:v", "copy",
        "-c:a", "aac",
        "-shortest",
        str(output_path)
    ], check=True)

    print(f"[OK] Created: {output_path}")
    return output_path
