#!/usr/bin/env python3
import os
import re
import subprocess
import sys
from pathlib import Path

CONTENT_DIR = os.getenv("CONTENT_DIR", "content")
CTA_PATTERN = re.compile(r"(?mi)^\s*CTA_PRIMARY\s*:\s*\S.+$")


def has_valid_cta(text: str) -> bool:
    return CTA_PATTERN.search(text) is not None


def synth_one_txt(txt_path: Path, voice: str) -> bool:
    wav_path = txt_path.with_suffix(".wav")
    if wav_path.exists():
        return False  # already present
    # macOS "say" outputs AIFF/CAF; we convert to WAV with afconvert
    aiff_path = txt_path.with_suffix(".aiff")
    # Read text to avoid "say -f" choking on unusual encodings
    text = txt_path.read_text(encoding="utf-8")
    # Write to temp file because "say" prefers files for long text
    tmp_txt = txt_path.with_suffix(".tmp.txt")
    tmp_txt.write_text(text, encoding="utf-8")
    try:
        subprocess.check_call(
            ["say", "-v", voice, "-f", str(tmp_txt), "-o", str(aiff_path)]
        )
        subprocess.check_call(
            [
                "afconvert",
                "-f",
                "WAVE",
                "-d",
                "LEI16",
                "-r",
                "22050",
                str(aiff_path),
                str(wav_path),
            ]
        )
    finally:
        if aiff_path.exists():
            aiff_path.unlink()
        if tmp_txt.exists():
            tmp_txt.unlink()
    return True


def main():
    if len(sys.argv) < 2:
        print("Usage: generate_wav_from_txt.py PACK_ID")
        sys.exit(2)
    pack_id = sys.argv[1]
    voice = os.getenv("TTS_VOICE", os.getenv("tts_voice", "Samantha"))

    narr_dir = Path(CONTENT_DIR) / pack_id / "narration"
    if not narr_dir.is_dir():
        print(f"❌ narration dir not found: {narr_dir}")
        sys.exit(1)

    txt_files = sorted([p for p in narr_dir.iterdir() if p.suffix.lower() == ".txt"])
    if not txt_files:
        print(f"❌ no .txt narration files in {narr_dir}")
        sys.exit(1)

    made = 0
    skipped = 0
    invalid = 0

    for txt in txt_files:
        text = txt.read_text(encoding="utf-8")
        if not has_valid_cta(text):
            print(f"⚠️  skip (no valid CTA_PRIMARY): {txt.name}")
            invalid += 1
            continue
        if txt.with_suffix(".wav").exists():
            skipped += 1
            continue
        try:
            if synth_one_txt(txt, voice):
                made += 1
                print(f"🎤 made: {txt.with_suffix('.wav').name}")
        except subprocess.CalledProcessError as e:
            print(f"❌ TTS failed for {txt.name}: {e}")
    print(f"Done. created={made} skipped_existing={skipped} invalid_no_cta={invalid}")


if __name__ == "__main__":
    main()
