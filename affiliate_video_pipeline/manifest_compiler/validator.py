import os, json, hashlib

def hash_file(path):
    if not os.path.exists(path): return None
    with open(path, 'rb') as f:
        return hashlib.md5(f.read()).hexdigest()

def validate_manifest(path):
    if not os.path.exists(path):
        print(f"❌ Manifest not found: {path}")
        return False

    with open(path) as f:
        manifest = json.load(f)

    errors = []

    # Check asset existence
    for asset_name, asset_path in manifest["assets"].items():
        if not os.path.exists(asset_path):
            errors.append(f"Missing asset: {asset_name} → {asset_path}")

    # Check hash integrity
    for asset_name, expected_hash in manifest["hashes"].items():
        actual_hash = hash_file(manifest["assets"].get(asset_name))
        if actual_hash != expected_hash:
            errors.append(f"Hash mismatch: {asset_name} → expected {expected_hash}, got {actual_hash}")

    # Check CTA timing logic
    if any(t > manifest["duration"] for t in manifest["cta_timing"]):
        errors.append("CTA timing exceeds video duration")

    # Check upload status values
    valid_status = {"pending", "uploaded", "failed"}
    for platform, status in manifest["upload_status"].items():
        if status not in valid_status:
            errors.append(f"Invalid upload status: {platform} → {status}")

    if errors:
        print(f"❌ Validation failed for {path}:")
        for err in errors:
            print(f"   - {err}")
        return False

    print(f"✅ Manifest valid: {path}")
    return True
