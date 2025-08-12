#!/usr/bin/env python3
import csv
import os
import subprocess
import sys

from _utils import ensure_dir, env_run_id, log

RUN_ID = env_run_id()


def run(cmd: list[str]) -> int:
    log(f"[{RUN_ID}] RUN | {' '.join(cmd)}")
    return subprocess.call(cmd)


def collect_summary() -> None:
    logs_dir = os.path.join("logs", f"run_{RUN_ID}")
    ensure_dir(logs_dir)
    ctas = os.path.join(logs_dir, "validate_ctas.csv")
    imgs = os.path.join(logs_dir, "match_images.csv")
    out = os.path.join(logs_dir, "audit_summary.csv")
    cta_by_pack = {}
    if os.path.isfile(ctas):
        with open(ctas, "r", encoding="utf-8") as f:
            for row in csv.DictReader(f):
                cta_by_pack[row["pack"]] = row
    rows = []
    if os.path.isfile(imgs):
        with open(imgs, "r", encoding="utf-8") as f:
            for row in csv.DictReader(f):
                pack = row["pack"]
                cta = cta_by_pack.get(pack, {})
                rows.append(
                    {
                        "run_id": RUN_ID,
                        "pack": pack,
                        "input_yaml_found": cta.get("input_yaml_found", ""),
                        "cta_changed": cta.get("changed", ""),
                        "cta_note": cta.get("note", ""),
                        "narration_count": row["narration_count"],
                        "images_matched": row["images_matched"],
                        "fallbacks_created": row["fallbacks_created"],
                        "images_missing_after": row["images_missing_after"],
                    }
                )
    else:
        packs_dir = "packs"
        if os.path.isdir(packs_dir):
            for pack_dir in sorted(os.listdir(packs_dir)):
                rows.append(
                    {
                        "run_id": RUN_ID,
                        "pack": pack_dir,
                        "input_yaml_found": cta_by_pack.get(pack_dir, {}).get(
                            "input_yaml_found", ""
                        ),
                        "cta_changed": cta_by_pack.get(pack_dir, {}).get("changed", ""),
                        "cta_note": cta_by_pack.get(pack_dir, {}).get("note", ""),
                        "narration_count": "",
                        "images_matched": "",
                        "fallbacks_created": "",
                        "images_missing_after": "",
                    }
                )
    with open(out, "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(
            f,
            fieldnames=[
                "run_id",
                "pack",
                "input_yaml_found",
                "cta_changed",
                "cta_note",
                "narration_count",
                "images_matched",
                "fallbacks_created",
                "images_missing_after",
            ],
        )
        w.writeheader()
        for r in rows:
            w.writerow(r)
    log(f"[{RUN_ID}] AUDIT | wrote {out}")


def main():
    ensure_dir(os.path.join("logs", f"run_{RUN_ID}"))
    if run([sys.executable, "scripts/validate_ctas.py"]) != 0:
        log(f"[{RUN_ID}] ERR | validate_ctas failed")
        sys.exit(1)
    if run([sys.executable, "scripts/match_images.py"]) != 0:
        log(f"[{RUN_ID}] ERR | match_images failed")
        sys.exit(1)
    collect_summary()


if __name__ == "__main__":
    main()
