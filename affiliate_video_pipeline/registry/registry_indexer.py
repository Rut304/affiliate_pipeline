import os
import csv

MANIFEST_DIR = "affiliate_video_pipeline/manifests"
INDEX_PATH = "affiliate_video_pipeline/registry/manifest_index.csv"

def generate_registry_index():
    manifests = [
        f for f in os.listdir(MANIFEST_DIR)
        if f.endswith("_manifest.json")
    ]

    with open(INDEX_PATH, "w", newline="") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["Manifest Filename"])
        for manifest in manifests:
            writer.writerow([manifest])

    return INDEX_PATH
