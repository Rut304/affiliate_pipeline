# pipeline/steps/repair_narration_cta.py
import os
import re
from typing import List, Tuple

CTA_PATTERN = re.compile(r'(?mi)^\s*CTA_PRIMARY\s*:\s*\S.+$')

def _has_valid_cta(text: str) -> bool:
    return CTA_PATTERN.search(text) is not None

def _ensure_trailing_newline(s: str) -> str:
    return s if s.endswith('\n') else s + '\n'

def repair_narration_cta(
    narr_dir: str,
    fallback_cta: str = "CTA_PRIMARY: Check out this product",
    make_backup: bool = True,
    dry_run: bool = False,
) -> Tuple[int, int, List[str]]:
    """
    Scan narration .txt files in narr_dir.
    If CTA_PRIMARY line is missing or malformed, append a valid fallback CTA line.

    Returns: (repaired_count, total_checked, repaired_files)
    """
    if not os.path.isdir(narr_dir):
        return 0, 0, []

    repaired = 0
    checked = 0
    repaired_files: List[str] = []

    for fname in sorted(os.listdir(narr_dir)):
        if not fname.lower().endswith(".txt"):
            continue
        fpath = os.path.join(narr_dir, fname)
        try:
            with open(fpath, "r", encoding="utf-8") as f:
                text = f.read()
        except UnicodeDecodeError:
            # Skip binary or non-text files defensively
            continue

        checked += 1

        if _has_valid_cta(text):
            continue

        # Prepare updated content
        updated = _ensure_trailing_newline(text) + _ensure_trailing_newline(fallback_cta)

        if not dry_run:
            if make_backup and not os.path.exists(fpath + ".bak"):
                with open(fpath + ".bak", "w", encoding="utf-8") as b:
                    b.write(text)
            with open(fpath, "w", encoding="utf-8") as f:
                f.write(updated)

        repaired += 1
        repaired_files.append(fname)

    return repaired, checked, repaired_files
