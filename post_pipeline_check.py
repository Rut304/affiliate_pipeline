# post_pipeline_check.py
from pathlib import Path


def check_output(pack_id: str) -> None:
    base_dir = Path("content") / pack_id
    narration_dir = base_dir / "narration"
    output_dir = base_dir / "output"
    issues = 0

    for txt_file in sorted(narration_dir.glob("product*.txt")):
        stem = txt_file.stem  # productX
        wav_file = narration_dir / f"{stem}.wav"
        mp4_file = output_dir / f"{stem}.mp4"

        # Voiceover check
        if not wav_file.exists():
            print(f"❌ {stem}.wav missing")
            issues += 1

        # Video check
        if not mp4_file.exists():
            print(f"❌ {stem}.mp4 missing")
            issues += 1

    if issues == 0:
        print("✅ All output videos present and mapped cleanly.")
    else:
        print(f"🔴 Found {issues} issue(s) in final output. Review recommended.")


if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("Usage: python post_pipeline_check.py <pack_id>")
        sys.exit(1)
    check_output(sys.argv[1])
