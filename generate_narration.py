#!/usr/bin/env python3
import argparse
import os
import yaml
import shutil
from pathlib import Path

def load_yaml(path):
    if not os.path.isfile(path):
        print(f"❌ Missing input.yaml: {path}")
        return {}
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)

def synthesize_narration(text: str, output_path: Path):
    # Placeholder synthesis logic—replace with actual TTS call or mock
    with open(output_path, "wb") as f:
        f.write(b"FAKE AUDIO DATA")  # Replace this with real audio generation
    print(f"🎙️ Synthesized: {output_path.name}")

def generate_pack_narration(pack_id: str, audio=True, overwrite=False, wpm=120):
    base_dir = Path("content") / pack_id
    yaml_path = base_dir / "input.yaml"

    # Preflight check
    if not yaml_path.is_file():
        print(f"❌ Skipping {pack_id}: missing {yaml_path}")
        return

    data = load_yaml(yaml_path)
    narration_dir = base_dir / "narration"
    narration_dir.mkdir(exist_ok=True, parents=True)

    # Ensure CTA_PRIMARY exists
    cta = data.get("CTA_PRIMARY", "").strip()
    if not cta:
        fallback_cta = "Check the link in the description for today’s offer!"
        print(f"⚠️ {pack_id}: Missing CTA_PRIMARY. Using fallback.")
        data["CTA_PRIMARY"] = fallback_cta
    else:
        print(f"✅ {pack_id}: Found CTA_PRIMARY.")

    # Generate mock narration files (replace with your actual logic)
    for i in range(1, 6):  # Example: nar1.txt to nar5.txt
        txt_file = narration_dir / f"nar{i}.txt"
        wav_file = narration_dir / f"nar{i}.wav"

        narration_text = f"This is narration {i} — {data['CTA_PRIMARY']}"

        # Write the narration TXT
        txt_file.write_text(narration_text, encoding="utf-8")

        # Generate audio file (placeholder)
        if audio and (overwrite or not wav_file.exists()):
            synthesize_narration(narration_text, wav_file)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("pack_id", help="Pack ID (folder under content/)")
    parser.add_argument("--audio", action="store_true", help="Generate audio files")
    parser.add_argument("--overwrite", action="store_true", help="Overwrite existing files")
    parser.add_argument("--wpm", type=int, default=120, help="Words per minute")
    args = parser.parse_args()

    generate_pack_narration(args.pack_id, audio=args.audio, overwrite=args.overwrite, wpm=args.wpm)

if __name__ == "__main__":
    main()
