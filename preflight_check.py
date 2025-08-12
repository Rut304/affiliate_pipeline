# preflight_check.py
import argparse
import sys
from pathlib import Path
from validate_narration import validate_narration  # importable function

def main():
    ap = argparse.ArgumentParser(description="Preflight gate for narration assets.")
    ap.add_argument("--narration-dir", default="narration", help="Directory of narration .txt files")
    ap.add_argument("--autopatch", action="store_true", help="Auto-insert [CTA_PRIMARY] if missing")
    args = ap.parse_args()

    n_dir = Path(args.narration_dir)
    if not n_dir.exists():
        print(f"[error] Narration directory not found: {n_dir}")
        sys.exit(2)

    results = validate_narration(str(n_dir), patch=args.autopatch)

    failures = {name: errs for name, errs in results.items() if errs}
    if failures:
        print("[preflight] Validation failed. See validation.log for full details.")
        for name, errs in failures.items():
            print(f"[fail] {name}: {'; '.join(errs)}")
        sys.exit(1)

    print("[preflight] Narration validation passed ✅")
    sys.exit(0)

if __name__ == "__main__":
    main()
