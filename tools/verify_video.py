
import sys
from moviepy.video.io.VideoFileClip import VideoFileClip

def verify_video(path):
    clip = VideoFileClip(path)
    print(f"Duration: {clip.duration:.2f}s")
    print(f"Resolution: {clip.size}")
    if clip.audio is None:
        print("No audio track found!")
        return False
    audio = clip.audio.to_soundarray(fps=22050)
    if audio.max() == 0:
        print("Audio track is silent!")
        return False
    print("Audio track present and non-silent.")
    return True

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python tools/verify_video.py <video_path>")
        sys.exit(1)
    video_path = sys.argv[1]
    verify_video(video_path)
