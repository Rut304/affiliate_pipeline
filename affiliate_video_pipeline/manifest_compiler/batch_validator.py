import json
import os

MANIFEST_DIR = "affiliate_video_pipeline/manifests"


def validate_all_manifests():
    results = {}
    for filename in os.listdir(MANIFEST_DIR):
        if filename.endswith("_manifest.json"):
            path = os.path.join(MANIFEST_DIR, filename)
            try:
                with open(path, "r") as f:
                    json.load(f)
                results[path] = "✅ Valid"
            except Exception as e:
                results[path] = f"❌ Invalid: {e}"
    return results
