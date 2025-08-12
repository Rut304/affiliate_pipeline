# sync_packs_to_content.py
from pathlib import Path
import shutil

PACKS_DIR = Path("packs")
CONTENT_DIR = Path("content")

def sync_packs(overwrite: bool = False):
    count = 0
    for pack_file in PACKS_DIR.glob("*.yaml"):
        pack_id = pack_file.stem
        target_dir = CONTENT_DIR / pack_id
        target_dir.mkdir(parents=True, exist_ok=True)
        target_file = target_dir / "input.yaml"

        if target_file.exists() and not overwrite:
            print(f"⏩ Skipped existing: {target_file}")
            continue

        shutil.copy2(pack_file, target_file)
        print(f"✅ Synced: {pack_file.name} → {target_file}")
        count += 1

    print(f"\n🔁 Sync complete: {count} packs updated.")

if __name__ == "__main__":
    import argparse
    ap = argparse.ArgumentParser(description="Sync packs/*.yaml into content/{id}/input.yaml for narration.")
    ap.add_argument("--overwrite", action="store_true", help="Overwrite existing input.yaml files in content/")
    args = ap.parse_args()
    sync_packs(overwrite=args.overwrite)
