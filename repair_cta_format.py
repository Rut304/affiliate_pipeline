# repair_cta_format.py
from pathlib import Path

import yaml


def load_yaml(yml_path):
    with open(yml_path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f) or {}


def repair_files(pack_id):
    pack_dir = Path("content") / pack_id
    narration_dir = pack_dir / "narration"
    products = load_yaml(pack_dir / "input.yaml").get("products", [])

    repaired = 0
    for i, txt_file in enumerate(sorted(narration_dir.glob("product*.txt"))):
        if i >= len(products):
            continue

        link = products[i].get("link", "https://example.com/deals")
        text = txt_file.read_text(encoding="utf-8")

        # Remove malformed tokens and append correct one
        fixed_text = text.split("[CTA_PRIMARY]")[0].strip()
        new_cta = f"[CTA_PRIMARY] Learn more at {link}"
        fixed_text += f"\n\n{new_cta}\n"

        txt_file.write_text(fixed_text, encoding="utf-8")
        print(f"✅ Repaired {txt_file.name}")
        repaired += 1

    print(f"🔧 Repaired {repaired} file(s)")


if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("Usage: python repair_cta_format.py <pack_id>")
        sys.exit(1)
    repair_files(sys.argv[1])
