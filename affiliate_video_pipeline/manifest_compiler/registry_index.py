import os, json, csv

def generate_registry_index(manifest_dir="affiliate_video_pipeline/manifests", out_path="affiliate_video_pipeline/registry/manifest_index.csv"):
    if not os.path.exists(manifest_dir):
        print(f"❌ Manifest directory not found: {manifest_dir}")
        return

    files = [f for f in os.listdir(manifest_dir) if f.endswith("_manifest.json")]
    if not files:
        print("⚠️ No manifest files found.")
        return

    rows = []
    for fname in files:
        path = os.path.join(manifest_dir, fname)
        with open(path) as f:
            manifest = json.load(f)

        row = {
            "pack_id": manifest.get("pack_id"),
            "title": manifest.get("title"),
            "duration": manifest.get("duration"),
            "version": manifest.get("version"),
            "last_modified": manifest.get("last_modified"),
            "amazon": manifest.get("upload_status", {}).get("amazon", ""),
            "youtube": manifest.get("upload_status", {}).get("youtube", ""),
            "s3": manifest.get("upload_status", {}).get("s3", "")
        }
        rows.append(row)

    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    with open(out_path, 'w', newline='') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=rows[0].keys())
        writer.writeheader()
        writer.writerows(rows)

    print(f"📊 Registry index written: {out_path}")
