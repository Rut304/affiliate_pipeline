#!/usr/bin/env python3
import argparse
import shutil
from pathlib import Path


def generate_cta_images(pack_id: str):
    base = Path("content") / pack_id
    images_dir = base / "images"
    overlays_dir = base / "cta_overlays"

    if not images_dir.is_dir():
        print(f"❌ Skipping {pack_id}: missing images directory {images_dir}")
        return

    overlays_dir.mkdir(parents=True, exist_ok=True)

    existing = list(overlays_dir.glob("*.jpg")) + list(overlays_dir.glob("*.png"))
    if existing:
        print(f"CTA overlays present for {pack_id}: {len(existing)} file(s).")
        return

    count = 0
    for src in sorted(images_dir.glob("*")):
        if src.suffix.lower() in {".jpg", ".jpeg", ".png"} and src.is_file():
            dst = overlays_dir / src.name
            if not dst.exists():
                shutil.copy2(src, dst)
                count += 1

    print(f"✅ Created {count} CTA overlay(s) for {pack_id}")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("pack_id", help="Pack folder name under content/")
    args = parser.parse_args()
    generate_cta_images(args.pack_id)


if __name__ == "__main__":
    main()
