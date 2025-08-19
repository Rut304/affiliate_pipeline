# sync_packs_to_content.py
import shutil
from pathlib import Path

PACKS_DIR = Path("packs")
CONTENT_DIR = Path("content")


def sync_packs(overwrite: bool = False):
    count = 0
    for pack_file in PACKS_DIR.glob("*.yaml"):
        pack_id = pack_file.stem
        target_dir = CONTENT_DIR / pack_id
        target_dir.mkdir(parents=True, exist_ok=True)
        target_file = target_dir / "input.yaml"

        if target_file.exists() and not overwrite:
            print(f"⏩ Skipped existing: {target_file}")
            continue

        shutil.copy2(pack_file, target_file)
        print(f"✅ Synced: {pack_file.name} → {target_file}")
        count += 1

    print(f"\n🔁 Sync complete: {count} packs updated.")


if __name__ == "__main__":
    import argparse

    ap = argparse.ArgumentParser(
        description="Sync packs/*.yaml into content/{id}/input.yaml for narration."
    )
    ap.add_argument(
        "--overwrite",
        action="store_true",
        help="Overwrite existing input.yaml files in content/",
    )
    args = ap.parse_args()
    sync_packs(overwrite=args.overwrite)

# filepath: tools/verify_video.py
import sys
from moviepy.editor import VideoFileClip


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
