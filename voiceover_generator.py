# voiceover_generator.py
import argparse, json
from pathlib import Path
import hashlib

def synthesize(text: str, output_path: Path) -> dict:
    # Simulated voiceover generator — replace with real API or TTS library
    duration_sec = max(6.0, round(len(text.split()) / 165.0 * 60.0, 2))
    audio_bytes = b"WAVDATA:" + text.encode("utf-8")
    output_path.write_bytes(audio_bytes)

    return {
        "id": output_path.stem,
        "text": text,
        "duration_sec": duration_sec,
        "hash": hashlib.md5(text.encode()).hexdigest()
    }

def generate_voiceovers(narration_dir: str, out_dir: str) -> list[Path]:
    n_dir = Path(narration_dir)
    o_dir = Path(out_dir)
    o_dir.mkdir(parents=True, exist_ok=True)
    written = []

    for txt in sorted(n_dir.glob("*.txt")):
        text = txt.read_text().strip()
        if "[CTA_PRIMARY]" not in text:
            print(f"[skip] {txt.name}: missing [CTA_PRIMARY]")
            continue

        wav_path = o_dir / f"{txt.stem}.wav"
        meta_path = o_dir / f"{txt.stem}.json"
        meta = synthesize(text, wav_path)
        meta_path.write_text(json.dumps(meta, indent=2))
        print(f"[voice] {wav_path.name} ({meta['duration_sec']}s)")
        written.append(wav_path)
    return written

def main():
    ap = argparse.ArgumentParser(description="Generate voiceovers from narration files.")
    ap.add_argument("--narration-dir", default="narration")
    ap.add_argument("--out", default="audio")
    args = ap.parse_args()
    generate_voiceovers(narration_dir=args.narration_dir, out_dir=args.out)

if __name__ == "__main__":
    main()
