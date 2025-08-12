# video_builder.py
import argparse
from pathlib import Path

def build_video(product_id: str, narration_path: Path, voice_path: Path, overlay_path: Path, image_path: Path, out_dir: Path):
    out_path = out_dir / f"{product_id}.mp4"
    # Simulated placeholder
    out_path.write_bytes(b"VIDEO:" + product_id.encode())
    print(f"[video] {out_path.name} from {voice_path.name}, {overlay_path.name}, {image_path.name if image_path.exists() else 'NO_IMAGE'}")
    return out_path

def assemble_videos(narration_dir: str, overlays_dir: str, audio_dir: str, image_dir: str, out_dir: str):
    n_dir = Path(narration_dir)
    o_dir = Path(overlays_dir)
    a_dir = Path(audio_dir)
    i_dir = Path(image_dir)
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)

    for txt in sorted(n_dir.glob("*.txt")):
        stem = txt.stem
        voice = a_dir / f"{stem}.wav"
        overlay = o_dir / f"{stem}.json"
        image = i_dir / f"{stem}.jpg"
        if not voice.exists() or not overlay.exists():
            print(f"[skip] {stem}: missing voice or overlay")
            continue
        build_video(stem, txt, voice, overlay, image, out)

def main():
    ap = argparse.ArgumentParser(description="Assemble video clips from narration, overlays, voice, and product image.")
    ap.add_argument("--narration-dir", default="narration")
    ap.add_argument("--overlays-dir", default="overlays")
    ap.add_argument("--audio-dir", default="audio")
    ap.add_argument("--image-dir", default="images")
    ap.add_argument("--out", default="videos")
    args = ap.parse_args()

    assemble_videos(
        narration_dir=args.narration_dir,
        overlays_dir=args.overlays_dir,
        audio_dir=args.audio_dir,
        image_dir=args.image_dir,
        out_dir=args.out
    )

if __name__ == "__main__":
    main()
