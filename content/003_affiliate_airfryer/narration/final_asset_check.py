# final_asset_check.py
from pathlib import Path
import re

def validate_assets(pack_id: str) -> None:
    narration_dir = Path("content") / pack_id / "narration"
    txt_files = sorted(narration_dir.glob("product*.txt"))
    errors = 0

    for txt_file in txt_files:
        base = txt_file.stem  # productX
        wav_file = narration_dir / f"{base}.wav"

        # Check CTA
        text = txt_file.read_text(encoding="utf-8")
        if "[CTA_PRIMARY]" not in text:
            print(f"❌ {txt_file.name} → missing [CTA_PRIMARY]")
            errors += 1

        # Check voiceover
        if not wav_file.exists():
            print(f"❌ {wav_file.name} → missing")
            errors += 1

    if errors == 0:
        print("✅ All product narration files and voiceovers validated.")
    else:
        print(f"🔴 {errors} issue(s) found. Please fix before running pipeline.")

if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("Usage: python final_asset_check.py <pack_id>")
        sys.exit(1)
    validate_assets(sys.argv[1])
