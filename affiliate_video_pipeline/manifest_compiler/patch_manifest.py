import os, json, hashlib
from datetime import datetime

def hash_file(path):
    if not os.path.exists(path): return None
    with open(path, 'rb') as f:
        return hashlib.md5(f.read()).hexdigest()

def patch_manifest(path):
    if not os.path.exists(path):
        print(f"❌ Manifest not found: {path}")
        return False

    with open(path) as f:
        manifest = json.load(f)

    updated = False
    new_hashes = {}

    for asset_name, asset_path in manifest["assets"].items():
        if os.path.exists(asset_path):
            new_hash = hash_file(asset_path)
            old_hash = manifest["hashes"].get(asset_name)
            if new_hash != old_hash:
                new_hashes[asset_name] = new_hash
                updated = True
        else:
            print(f"⚠️ Missing asset: {asset_name} → {asset_path}")

    if updated:
        manifest["hashes"].update(new_hashes)
        manifest["last_modified"] = datetime.utcnow().isoformat()
        with open(path, 'w') as f:
            json.dump(manifest, f, indent=2)
        print(f"🔧 Manifest patched: {path}")
        for k, v in new_hashes.items():
            print(f"   - Updated hash: {k} → {v}")
        return True
    else:
        print(f"✅ No changes needed: {path}")
        return False
