import json
import os

MANIFEST_DIR = "affiliate_video_pipeline/manifests"


def patch_all_manifests():
    patched = []
    for filename in os.listdir(MANIFEST_DIR):
        if filename.endswith("_manifest.json"):
            path = os.path.join(MANIFEST_DIR, filename)
            with open(path, "r") as f:
                data = json.load(f)

            # Simulate patch logic
            original = json.dumps(data, sort_keys=True)
            patched_data = data  # No-op patch

            if json.dumps(patched_data, sort_keys=True) != original:
                with open(path, "w") as f:
                    json.dump(patched_data, f, indent=2)
                patched.append(path)
    return patched
