import json
import os
from pathlib import Path


def validate_manifest(pack_id: str) -> str:
    manifest_path = f"affiliate_video_pipeline/manifests/{pack_id}_manifest.json"
    if not os.path.exists(manifest_path):
        return "❌ Manifest missing"
    try:
        with open(manifest_path, "r") as f:
            json.load(f)
        return "✅ Valid"
    except Exception as e:
        return f"❌ Invalid: {e}"


def validate_images(pack_id: str) -> str:
    manifest_path = f"affiliate_video_pipeline/manifests/{pack_id}_manifest.json"
    images_dir = f"content/{pack_id}/images"
    if not os.path.exists(images_dir):
        return "❌ Images folder missing"

    try:
        with open(manifest_path, "r") as f:
            manifest = json.load(f)
        expected = set(item["image"] for item in manifest.get("items", []))
        actual = set(os.listdir(images_dir))
        missing = expected - actual
        if missing:
            return f"❌ Missing images: {', '.join(missing)}"
        return "✅ Found"
    except Exception as e:
        return f"❌ Error validating images: {e}"


def validate_narration(pack_id: str) -> str:
    narration_path = f"narration/{pack_id}.json"
    if not os.path.exists(narration_path):
        return "❌ Narration file missing"
    try:
        with open(narration_path, "r") as f:
            data = json.load(f)
        if not isinstance(data, list) or not all("text" in item for item in data):
            return "❌ Invalid narration schema"
        return "✅ Found"
    except Exception as e:
        return f"❌ Error validating narration: {e}"


def validate_output_dir(pack_id: str) -> str:
    output_dir = f"packs/{pack_id}"
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    return "✅ Ready"


def validate_pack(pack_id: str) -> dict:
    results = {
        "manifest": validate_manifest(pack_id),
        "images": validate_images(pack_id),
        "narration": validate_narration(pack_id),
        "output_dir": validate_output_dir(pack_id),
    }

    if all(val.startswith("✅") for val in results.values()):
        results["status"] = "✅ Pack is batch-ready"
    else:
        results["status"] = "❌ Pack is not ready"

    return results
