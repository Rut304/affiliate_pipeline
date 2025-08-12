import os, json, hashlib
from datetime import datetime

def hash_file(path):
    if not os.path.exists(path): return None
    with open(path, 'rb') as f:
        return hashlib.md5(f.read()).hexdigest()

def compile_manifest(pack_id, title, duration, cta_timing, asset_paths, upload_status, version="v1.0.0"):
    manifest = {
        "pack_id": pack_id,
        "title": title,
        "duration": duration,
        "cta_timing": cta_timing,
        "assets": asset_paths,
        "hashes": {k: hash_file(v) for k, v in asset_paths.items()},
        "upload_status": upload_status,
        "last_modified": datetime.utcnow().isoformat(),
        "version": version
    }
    out_path = f"affiliate_video_pipeline/manifests/{pack_id}_manifest.json"
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    with open(out_path, 'w') as f:
        json.dump(manifest, f, indent=2)
    return out_path
