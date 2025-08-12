import shutil
import subprocess
from pathlib import Path
from typing import Dict, List

MIN_LENGTH = 35
PATCH_TEXT = " Discover why this pick stands out."

def clean_text(text: str) -> str:
    # Remove placeholder tokens like [CTA_PRIMARY], [LINK], etc. without regex.
    out = []
    skipping = 0
    for ch in text:
        if ch == '[':
            skipping += 1
            continue
        if ch == ']':
            if skipping > 0:
                skipping -= 1
            continue
        if skipping == 0:
            out.append(ch)
    text = "".join(out)
    # Collapse whitespace
    text = " ".join(text.split())
    return text.strip()

def ensure_ffmpeg() -> str:
    exe = shutil.which("ffmpeg")
    if not exe:
        raise RuntimeError("ffmpeg not found. Install with: brew install ffmpeg")
    return exe

def tts_to_wav(text: str, wav_path: Path, voice: str = "Samantha", sample_rate: int = 16000) -> None:
    """
    Use macOS 'say' to synthesize AIFF, then convert to 16kHz mono WAV via ffmpeg.
    Falls back to default voice if the specified voice isn't available.
    """
    wav_path.parent.mkdir(parents=True, exist_ok=True)
    aiff_path = wav_path.with_suffix(".aiff")

    try:
        subprocess.run(["say", "-v", voice, text, "-o", str(aiff_path)], check=True)
    except subprocess.CalledProcessError:
        subprocess.run(["say", text, "-o", str(aiff_path)], check=True)

    ffmpeg = ensure_ffmpeg()
    subprocess.run(
        [ffmpeg, "-y", "-i", str(aiff_path), "-ar", str(sample_rate), "-ac", "1", str(wav_path)],
        check=True
    )

    try:
        aiff_path.unlink()
    except Exception:
        pass

def validate_narration(narration_dir: str, patch: bool = False) -> Dict[str, List[str]]:
    """
    Validate nar*.txt files:
      - Clean placeholders
      - Enforce length >= MIN_LENGTH
      - If patch=True, append filler and regenerate WAV via TTS
    Returns: dict of filename -> list of error strings (empty list means OK)
    """
    dir_path = Path(narration_dir)
    files = sorted(dir_path.glob("nar*.txt"))
    results: Dict[str, List[str]] = {}

    for txt_file in files:
        fname = txt_file.name
        errors: List[str] = []

        raw_text = txt_file.read_text(encoding="utf-8")
        safe_text = clean_text(raw_text)

        if not safe_text:
            errors.append("empty after cleaning")
            if patch:
                safe_text = "This pick offers practical performance and value." + PATCH_TEXT

        if len(safe_text) < MIN_LENGTH:
            errors.append(f"too short ({len(safe_text)} < {MIN_LENGTH})")
            if patch:
                safe_text = (safe_text + PATCH_TEXT).strip()
                txt_file.write_text(safe_text, encoding="utf-8")
                print(f"📎 Patched {fname} to meet length threshold.")

        if patch:
            wav_file = txt_file.with_suffix(".wav")
            try:
                tts_to_wav(safe_text, wav_file)
                print(f"🎤 Rebuilt: {wav_file.name}")
            except subprocess.CalledProcessError as e:
                errors.append("speech synthesis failed")
                print(f"❌ TTS failed for {fname}: {e}")
            except Exception as e:
                errors.append(f"audio convert failed: {e}")
                print(f"❌ Audio conversion failed for {fname}: {e}")

        results[fname] = errors

    return results

if __name__ == "__main__":
    import argparse
    ap = argparse.ArgumentParser(description="Validate and optionally patch narration files.")
    ap.add_argument("narration_dir", help="Directory containing nar*.txt files")
    ap.add_argument("--patch", action="store_true", help="Patch short text and regenerate WAV")
    args = ap.parse_args()
    out = validate_narration(args.narration_dir, patch=args.patch)
    total = len(out)
    fails = sum(1 for v in out.values() if v)
    print(f"Done: {total - fails} OK, {fails} FAIL")
