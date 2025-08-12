#!/usr/bin/env python3
import os
import re
import sys
import argparse
import subprocess
from pathlib import Path
from typing import List, Tuple

# -----------------------------
# Configuration (env-overridable)
# -----------------------------
PACKS_DIR = os.getenv("PACKS_DIR", "packs")
CONTENT_DIR = os.getenv("CONTENT_DIR", "content")
AUTO_REPAIR_CTA_DEFAULT = os.getenv("AUTO_REPAIR_CTA", "1") not in ("0", "false", "False")
GLOBAL_FALLBACK_CTA = os.getenv("FALLBACK_CTA", "CTA_PRIMARY: Check out this product")

# -----------------------------
# CTA repair utility (idempotent)
# -----------------------------
_CTA_PATTERN = re.compile(r"(?mi)^\s*CTA_PRIMARY\s*:\s*\S.+$")

def _has_valid_cta(text: str) -> bool:
    return _CTA_PATTERN.search(text) is not None

def _ensure_trailing_newline(s: str) -> str:
    return s if s.endswith("\n") else s + "\n"

def repair_narration_cta(
    narr_dir: Path,
    fallback_cta: str,
    make_backup: bool = True,
    dry_run: bool = False,
) -> Tuple[int, int, List[str]]:
    if not narr_dir.is_dir():
        return 0, 0, []
    repaired = 0
    checked = 0
    repaired_files: List[str] = []
    for fpath in sorted(narr_dir.iterdir()):
        if not (fpath.is_file() and fpath.suffix.lower() == ".txt"):
            continue
        try:
            text = fpath.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        checked += 1
        if _has_valid_cta(text):
            continue
        updated = _ensure_trailing_newline(text) + _ensure_trailing_newline(fallback_cta)
        if not dry_run:
            if make_backup:
                bak = fpath.with_suffix(fpath.suffix + ".bak")
                if not bak.exists():
                    bak.write_text(text, encoding="utf-8")
            fpath.write_text(updated, encoding="utf-8")
        repaired += 1
        repaired_files.append(fpath.name)
    return repaired, checked, repaired_files

# -----------------------------
# Pack discovery
# -----------------------------
def get_all_pack_ids() -> List[str]:
    pack_dir = Path(PACKS_DIR)
    if not pack_dir.exists():
        return []
    return [p.name for p in pack_dir.iterdir() if p.is_dir()]

# -----------------------------
# Subprocess runner
# -----------------------------
def run_step(script: str, pack_id: str) -> int:
    cmd = [sys.executable, script, pack_id]
    return subprocess.run(cmd).returncode

# -----------------------------
# Fallback CTA selection
# -----------------------------
def choose_fallback_cta(pack_id: str) -> str:
    pid = pack_id.lower()
    if "airfryer" in pid:
        return "CTA_PRIMARY: Check out this airfryer"
    if "blender" in pid:
        return "CTA_PRIMARY: Blend smarter with this pick"
    if "coffee" in pid or "espresso" in pid:
        return "CTA_PRIMARY: Brew better—see this coffee gear"
    return GLOBAL_FALLBACK_CTA

# -----------------------------
# Per-pack pipeline
# -----------------------------
def run_pipeline_for(pack_id: str, auto_repair_cta: bool = True) -> None:
    print(f"\n▶ Running pipeline for: {pack_id}")

    run_step("validate_pack.py", pack_id)
    run_step("generate_narration.py", pack_id)

    # Auto-repair CTA before narration validation / TTS
    narr_dir = Path(CONTENT_DIR) / pack_id / "narration"
    if auto_repair_cta and narr_dir.exists():
        fallback_line = choose_fallback_cta(pack_id)
        repaired, checked, _ = repair_narration_cta(
            narr_dir=narr_dir,
            fallback_cta=fallback_line,
            make_backup=True,
            dry_run=False,
        )
        if checked == 0:
            print(f"❌ No narration .txt files found in {narr_dir}")
        elif repaired > 0:
            print(f"🛠 Repaired {repaired}/{checked} narration file(s) missing CTA_PRIMARY in {pack_id}")
        else:
            print(f"✅ Narration CTA_PRIMARY already valid in {pack_id} ({checked} file(s) checked)")

    run_step("validate_narration.py", pack_id)

    # Generate WAVs from narration .txt (macOS TTS)
    run_step("scripts/generate_wav_from_txt.py", pack_id)

    run_step("generate_cta_images.py", pack_id)
    run_step("assemble_videos.py", pack_id)

# -----------------------------
# CLI
# -----------------------------
def parse_args():
    import argparse
    parser = argparse.ArgumentParser(description="Run affiliate pipeline for one or all packs.")
    parser.add_argument("pack_id", nargs="?", help="Optional pack ID. If omitted, run for all packs.")
    parser.add_argument("--no-auto-repair-cta", action="store_true", help="Disable auto-repair of CTA_PRIMARY in narration .txt files")
    return parser.parse_args()

def main(pack_id=None):
    args = parse_args()
    auto_repair_cta = AUTO_REPAIR_CTA_DEFAULT and (not args.no_auto_repair_cta)
    if args.pack_id:
        run_pipeline_for(args.pack_id, auto_repair_cta=auto_repair_cta)
    else:
        for pack in get_all_pack_ids():
            run_pipeline_for(pack, auto_repair_cta=auto_repair_cta)

if __name__ == "__main__":
    main()
