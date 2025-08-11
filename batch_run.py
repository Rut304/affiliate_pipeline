import os
import sys
import json
import argparse
import logging
from datetime import datetime

DEFAULT_CONTENT_DIR = "content"
DEFAULT_EXPORT_DIR = "exports"
VALID_IMAGE_EXTS = {".jpg", ".jpeg", ".png", ".webp"}

def setup_logging(verbose: bool):
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format="%(asctime)s | %(levelname)-7s | %(message)s",
        datefmt="%H:%M:%S",
    )

def list_packs(content_dir: str):
    if not os.path.isdir(content_dir):
        logging.error(f"Content dir not found: {content_dir}")
        return []
    # Only include subdirectories
    packs = [d for d in os.listdir(content_dir) if os.path.isdir(os.path.join(content_dir, d))]
    # Sort numerically when possible, otherwise lexicographically
    def sort_key(name: str):
        try:
            return (0, int(name.split("_", 1)[0]))
        except Exception:
            return (1, name)
    return sorted(packs, key=sort_key)

def load_metadata(pack_path: str):
    meta_path = os.path.join(pack_path, "metadata.json")
    if not os.path.isfile(meta_path):
        return None, f"Missing metadata.json at {meta_path}"
    try:
        with open(meta_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        return data, None
    except Exception as e:
        return None, f"Failed to parse metadata.json: {e}"

def collect_images(images_dir: str):
    files = []
    if os.path.isdir(images_dir):
        for f in os.listdir(images_dir):
            _, ext = os.path.splitext(f.lower())
            if ext in VALID_IMAGE_EXTS:
                files.append(os.path.join(images_dir, f))
    return sorted(files)

def validate_pack(content_dir: str, pack_name: str, metadata: dict):
    pack_path = os.path.join(content_dir, pack_name)
    warnings = []
    errors = []

    # Required metadata keys
    required_keys = ["title", "cta", "theme", "image_count", "narration_file", "text_file"]
    for k in required_keys:
        if k not in metadata:
            errors.append(f"metadata.json missing key: {k}")

    # Resolve expected paths
    narration_file = metadata.get("narration_file", "narration.mp3")
    text_file = metadata.get("text_file", "script.txt")
    narration_path = os.path.join(pack_path, narration_file)
    text_path = os.path.join(pack_path, text_file)
    images_dir = os.path.join(pack_path, "images")

    # File presence checks
    if not os.path.isfile(text_path):
        errors.append(f"Missing script text file: {text_path}")
    if not os.path.isfile(narration_path):
        warnings.append(f"Missing narration file: {narration_path}")

    images = collect_images(images_dir)
    expected_images = metadata.get("image_count", 0)
    if expected_images and len(images) < expected_images:
        warnings.append(f"Images found ({len(images)}) < image_count ({expected_images}) in {images_dir}")

    return {
        "pack_path": pack_path,
        "narration_path": narration_path,
        "text_path": text_path,
        "images_dir": images_dir,
        "images": images,
        "warnings": warnings,
        "errors": errors,
    }

def simulate_export(export_dir: str, pack_name: str, metadata: dict):
    pack_export_dir = os.path.join(export_dir, pack_name)
    os.makedirs(pack_export_dir, exist_ok=True)
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    outfile = os.path.join(pack_export_dir, f"video.txt")
    with open(outfile, "w", encoding="utf-8") as f:
        f.write(
            f"Exported video\n"
            f"Title: {metadata.get('title')}\n"
            f"CTA: {metadata.get('cta')}\n"
            f"Theme: {metadata.get('theme')}\n"
            f"Timestamp: {stamp}\n"
        )
    return outfile

def should_process(pack_name: str, only_set, skip_set):
    if only_set and pack_name not in only_set:
        return False
    if skip_set and pack_name in skip_set:
        return False
    return True

def parse_csv_set(value: str):
    if not value:
        return set()
    return set([v.strip() for v in value.split(",") if v.strip()])

def main():
    parser = argparse.ArgumentParser(description="Affiliate content batch runner")
    parser.add_argument("--content-dir", default=DEFAULT_CONTENT_DIR, help="Content directory")
    parser.add_argument("--export-dir", default=DEFAULT_EXPORT_DIR, help="Export directory")
    parser.add_argument("--only", default="", help="Comma-separated pack names to include (e.g., 002_affiliate_blender)")
    parser.add_argument("--skip", default="", help="Comma-separated pack names to skip")
    parser.add_argument("--dry-run", action="store_true", help="Validate only; do not write exports")
    parser.add_argument("--verbose", action="store_true", help="Verbose logging")
    parser.add_argument("--fail-on-warn", action="store_true", help="Treat warnings as failures")
    args = parser.parse_args()

    setup_logging(args.verbose)
    only_set = parse_csv_set(args.only)
    skip_set = parse_csv_set(args.skip)

    content_dir = args.content_dir
    export_dir = args.export_dir
    os.makedirs(export_dir, exist_ok=True)

    packs = list_packs(content_dir)
    if not packs:
        logging.warning("No packs found.")
        sys.exit(0)

    summary = []
    for pack_name in packs:
        if not should_process(pack_name, only_set, skip_set):
            logging.debug(f"Skipping (filtered): {pack_name}")
            summary.append((pack_name, "SKIPPED (filtered)"))
            continue

        pack_path = os.path.join(content_dir, pack_name)
        metadata, meta_err = load_metadata(pack_path)
        if meta_err:
            logging.warning(f"{pack_name}: {meta_err}")
            summary.append((pack_name, "NO METADATA"))
            continue

        check = validate_pack(content_dir, pack_name, metadata)
        for w in check["warnings"]:
            logging.warning(f"{pack_name}: {w}")
        for e in check["errors"]:
            logging.error(f"{pack_name}: {e}")

        if check["errors"]:
            summary.append((pack_name, "FAILED (errors)"))
            continue
        if args.fail_on_warn and check["warnings"]:
            summary.append((pack_name, "FAILED (warnings as errors)"))
            continue

        if args.dry_run:
            logging.info(f"{pack_name}: DRY RUN OK — would export to {os.path.join(export_dir, pack_name)}")
            summary.append((pack_name, "DRY-RUN OK"))
            continue

        outfile = simulate_export(export_dir, pack_name, metadata)
        logging.info(f"{pack_name}: Exported -> {outfile}")
        summary.append((pack_name, "EXPORTED"))

    # Summary
    print("\n=== Batch Summary ===")
    max_name = max((len(n) for (n, _) in summary), default=10)
    for name, status in summary:
        print(f"{name.ljust(max_name)}  |  {status}")

if __name__ == "__main__":
    main()
