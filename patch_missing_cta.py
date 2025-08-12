# patch_missing_cta.py
import re
from pathlib import Path

import yaml


def load_yaml(yml_path: Path) -> dict:
    with open(yml_path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f) or {}


def patch_product_files(pack_id: str) -> int:
    narration_dir = Path("content") / pack_id / "narration"
    yml_path = Path("content") / pack_id / "input.yaml"
    data = load_yaml(yml_path)
    products = data.get("products") or []

    patched = 0
    for txt_file in sorted(narration_dir.glob("nar*.txt")):
        # Extract numeric index from filename
        match = re.search(r"nar(\d+)\.txt", txt_file.name)
        if not match:
            print(f"⚠️ Skipping unrecognized file: {txt_file.name}")
            continue

        index = int(match.group(1)) - 1  # nar1.txt → index 0
        product = products[index] if index < len(products) else {}
        link = product.get("link", "https://example.com/deals")

        text = txt_file.read_text(encoding="utf-8")
        if "[CTA_PRIMARY]" in text:
            continue

        cta = f"[CTA_PRIMARY] Learn more at {link}"
        new_text = text.strip() + "\n\n" + cta + "\n"
        txt_file.write_text(new_text, encoding="utf-8")
        print(f"📎 Patched {txt_file.name} → {cta}")
        patched += 1

    if patched == 0:
        print("✅ All nar*.txt files contain CTA tokens.")
    else:
        print(f"🔧 Patched {patched} file(s) with CTA lines.")

    return patched


if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("Usage: python patch_missing_cta.py <pack_id>")
        sys.exit(1)
    patch_product_files(sys.argv[1])
