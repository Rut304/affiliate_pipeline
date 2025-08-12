import os
import csv
from affiliate_video_pipeline.validate_batch_ready import validate_pack

INDEX_PATH = "affiliate_video_pipeline/registry/batch_ready_index.csv"

def generate_batch_ready_index():
    content_dir = "content"
    pack_ids = [
        name for name in os.listdir(content_dir)
        if os.path.isdir(os.path.join(content_dir, name))
    ]

    rows = []
    for pack_id in sorted(pack_ids):
        result = validate_pack(pack_id)
        rows.append([
            pack_id,
            result["manifest"],
            result["images"],
            result["narration"],
            result["output_dir"],
            result["status"]
        ])

    with open(INDEX_PATH, "w", newline="") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["Pack ID", "Manifest", "Images", "Narration", "Output Dir", "Status"])
        writer.writerows(rows)

    print(f"📊 Batch-ready index written: {INDEX_PATH}")
