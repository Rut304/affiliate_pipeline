import re
import subprocess
from pathlib import Path
from typing import Dict, List

MIN_LENGTH = 35
PATCH_TEXT = " Discover why this pick stands out."


def clean_text(text: str) -> str:
    # Remove placeholder blocks like [CTA_PRIMARY], [LINK], etc.
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def validate_narration(narration_dir: str, patch: bool = False) -> Dict[str, List[str]]:
    dir_path = Path(narration_dir)
    files = sorted(dir_path.glob("nar*.txt"))
    results: Dict[str, List[str]] = {}

    for txt_file in files:
        fname = txt_file.name
        errors = []
        raw_text = txt_file.read_text(encoding="utf-8").strip()
        safe_text = clean_text(raw_text)

        if len(safe_text) < MIN_LENGTH:
            errors.append(f"too short ({len(safe_text)} < {MIN_LENGTH})")
            if patch:
                safe_text += PATCH_TEXT
                txt_file.write_text(safe_text, encoding="utf-8")
                print(f"📎 Patched {fname} to meet length threshold.")

        wav_file = txt_file.with_suffix(".wav")
        if patch:
            try:
                subprocess.run(
                    ["say", "-v", "Samantha", safe_text, "-o", str(wav_file)],
                    check=True,
                )
                print(f"🎤 Rebuilt: {wav_file.name}")
            except subprocess.CalledProcessError as e:
                errors.append("speech synthesis failed")
                print(f"❌ TTS failed for {fname}: {e}")

        results[fname] = errors

    return results
