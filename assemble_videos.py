# assemble_videos.py
import argparse
import shutil
import subprocess
from pathlib import Path
import re

IMG_EXTS = {".jpg", ".jpeg", ".png"}
NUM_RE = re.compile(r"nar(\d+)\.wav$", re.IGNORECASE)

def ffmpeg_or_die():
    exe = shutil.which("ffmpeg")
    if not exe:
        raise SystemExit("❌ ffmpeg not found. Install with: brew install ffmpeg")
    return exe

def pick_image(pack_dir: Path, idx: int, use_cta: bool) -> Path | None:
    name = f"img{idx}"
    # Prefer CTA dir if requested
    dirs = []
    if use_cta:
        dirs.append(pack_dir / "images_cta")
    dirs.append(pack_dir / "images")

    for d in dirs:
        for ext in IMG_EXTS:
            p = d / f"{name}{ext}"
            if p.exists():
                return p
    return None

def build_one(ffmpeg: str, image: Path, audio: Path, out: Path):
    out.parent.mkdir(parents=True, exist_ok=True)
    cmd = [
        ffmpeg, "-y",
        "-loop", "1", "-i", str(image),
        "-i", str(audio),
        "-c:v", "libx264", "-tune", "stillimage",
        "-c:a", "aac", "-b:a", "128k",
        "-pix_fmt", "yuv420p",
        "-shortest",
        "-movflags", "+faststart",
        str(out),
    ]
    subprocess.run(cmd, check=True)

def concat_all(ffmpeg: str, vdir: Path, outputs: list[Path], combined: Path):
    # Write list file for concat demuxer
    list_path = vdir / "list.txt"
    with list_path.open("w", encoding="utf-8") as f:
        for p in outputs:
            f.write(f"file '{p.name}'\n")

    cmd = [
        ffmpeg, "-y",
        "-f", "concat", "-safe", "0",
        "-i", str(list_path),
        "-c", "copy",
        str(combined),
    ]
    subprocess.run(cmd, check=True)

def assemble(pack_id: str, use_cta: bool):
    ffmpeg = ffmpeg_or_die()
    pack_dir = Path("content") / pack_id
    narr_dir = pack_dir / "narration"
    vdir = pack_dir / "video"
    vdir.mkdir(parents=True, exist_ok=True)

    wavs = sorted(narr_dir.glob("nar*.wav"))
    if not wavs:
        raise SystemExit(f"❌ No WAV files found in {narr_dir}")

    outputs: list[Path] = []
    for w in wavs:
        m = NUM_RE.search(w.name)
        if not m:
            print(f"⚠️ Skipping {w.name} (no index)")
            continue
        idx = int(m.group(1))
        img = pick_image(pack_dir, idx, use_cta=use_cta)
        if not img:
            print(f"❌ No matching image found for index {idx} (looked for img{idx}.*)")
            continue
        out = vdir / f"nar{idx}.mp4"
        print(f"🎬 Building {out.name} from {img.name} + {w.name}")
        build_one(ffmpeg, img, w, out)
        outputs.append(out)

    if not outputs:
        raise SystemExit("❌ No videos were produced.")

    combined = vdir / "combined.mp4"
    print(f"📼 Concatenating {len(outputs)} clips into {combined.name}")
    concat_all(ffmpeg, vdir, outputs, combined)
    print("✅ Video assembly complete.")

def main():
    ap = argparse.ArgumentParser(description="Assemble videos for a pack from images and narration audio.")
    ap.add_argument("pack_id", help="Pack under content/, e.g., 003_affiliate_airfryer")
    ap.add_argument("--use-cta", action="store_true", help="Use CTA overlays instead of raw images if available")
    args = ap.parse_args()
    assemble(args.pack_id, use_cta=args.use_cta)

if __name__ == "__main__":
    main()
