# validate_pack.py
import argparse
from pathlib import Path
import yaml
from typing import Dict, List, Tuple
import sys

# Reuse narration validator from project root
import validate_narration as narr

def load_yaml(path: Path) -> dict:
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f) or {}

def check_images(pack_dir: Path, products: list) -> Tuple[int, List[str]]:
    missing = []
    img_dir = pack_dir / "images"
    for p in products:
        name = p.get("image")
        if not name or not (img_dir / name).exists():
            missing.append(name or "<missing name>")
    return (len(products) - len(missing), missing)

def check_overlays(pack_dir: Path, products: list) -> Tuple[int, List[str]]:
    missing = []
    cta_dir = pack_dir / "images_cta"
    for p in products:
        name = p.get("image")
        if not name or not (cta_dir / name).exists():
            missing.append(name or "<missing name>")
    return (len(products) - len(missing), missing)

def check_videos(pack_dir: Path) -> Tuple[int, List[str]]:
    vdir = pack_dir / "video"
    if not vdir.exists():
        return (0, ["<video dir missing>"])
    vids = sorted(vdir.glob("*.mp4"))
    return (len(vids), [v.name for v in vids])

def check_product_cta(product_dir: Path) -> List[str]:
    issues = []
    for txt_file in sorted(product_dir.glob("product*.txt")):
        text = txt_file.read_text(encoding="utf-8")
        if "[CTA_PRIMARY]" not in text:
            issues.append(txt_file.name)
    return issues

def print_section(title: str):
    print("\n" + "="*len(title))
    print(title)
    print("="*len(title))

def validate_pack(pack_id: str, require_cta: bool, require_video: bool, patch_narr: bool) -> int:
    pack_dir = Path("content") / pack_id
    yml = pack_dir / "input.yaml"
    if not yml.exists():
        print(f"❌ Missing input.yaml: {yml}")
        return 2

    data = load_yaml(yml)
    products = data.get("products") or []
    if not products:
        print("❌ No products found in input.yaml")
        return 2

    # Product CTA validation
    print_section("Product CTA Check")
    cta_issues = check_product_cta(pack_dir / "narration")
    if cta_issues:
        for fname in cta_issues:
            print(f"❌ {fname}: missing [CTA_PRIMARY]")
        print("❌ Pack FAILED: CTA token check failed.")
        return 1
    else:
        print("CTA tokens OK in all product*.txt files")

    # Images
    print_section("Images")
    ok_imgs, missing_imgs = check_images(pack_dir, products)
    if missing_imgs:
        for m in missing_imgs:
            print(f"❌ Missing image: {m}")
    print(f"Images OK: {ok_imgs}/{len(products)}")

    # CTA overlays
    print_section("CTA overlays")
    ok_cta, missing_cta = check_overlays(pack_dir, products)
    if missing_cta:
        for m in missing_cta:
            print(f"⚠️ Missing CTA overlay: {m}")
    print(f"CTA OK: {ok_cta}/{len(products)}")

    # Narration
    print_section("Narration")
    narr_dir = pack_dir / "narration"
    narr_results = narr.validate_narration(str(narr_dir), patch=patch_narr)
    n_total = len(narr_results)
    n_fail = sum(1 for errs in narr_results.values() if errs)
    n_ok = n_total - n_fail
    for fname, errs in narr_results.items():
        if errs:
            print(f"❌ {fname}: {', '.join(errs)}")
    print(f"Narration OK: {n_ok}/{n_total}")

    # Video
    print_section("Video")
    v_ok, v_list = check_videos(pack_dir)
    if v_ok:
        for v in v_list:
            print(f"🎬 {v}")
    else:
        print("⚠️ No videos found")

    # Exit logic
    hard_fail = 0
    if ok_imgs < len(products): hard_fail = 1
    if n_ok < len(products): hard_fail = 1
    if require_cta and ok_cta < len(products): hard_fail = 1
    if require_video and v_ok < len(products): hard_fail = 1

    if hard_fail:
        print("\n❌ Pack FAILED required checks.")
        return 1
    else:
        print("\n✅ Pack PASSED required checks.")
        return 0

def main():
    ap = argparse.ArgumentParser(description="Validate a content pack end-to-end.")
    ap.add_argument("pack_id", help="Pack under content/, e.g., 003_affiliate_airfryer")
    ap.add_argument("--require-cta", action="store_true", help="Fail if CTA overlays missing")
    ap.add_argument("--require-video", action="store_true", help="Fail if videos missing")
    ap.add_argument("--patch-narr", action="store_true", help="Patch missing CTA in narration")
    args = ap.parse_args()
    code = validate_pack(args.pack_id, args.require_cta, args.require_video, args.patch_narr)
    raise SystemExit(code)

if __name__ == "__main__":
    main()

