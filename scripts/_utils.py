import os, sys, csv, time, shutil
from typing import Any, Dict, Optional
import yaml

def timestamp() -> str:
    return time.strftime("%Y%m%d_%H%M%S")

def ensure_dir(path: str) -> None:
    os.makedirs(path, exist_ok=True)

def load_yaml(path: str) -> Dict[str, Any]:
    with open(path, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f) or {}
    if not isinstance(data, dict):
        raise ValueError(f"YAML at {path} is not a mapping")
    return data

def dump_yaml(path: str, data: Dict[str, Any]) -> None:
    tmp = f"{path}.tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        yaml.safe_dump(data, f, sort_keys=False, allow_unicode=True)
    os.replace(tmp, path)

def list_packs(packs_root: str) -> list[str]:
    if not os.path.isdir(packs_root):
        return []
    return sorted([os.path.join(packs_root, d) for d in os.listdir(packs_root)
                   if os.path.isdir(os.path.join(packs_root, d))])

def find_files(root: str, exts: tuple[str, ...]) -> list[str]:
    out = []
    for dirpath, _, files in os.walk(root):
        for fn in files:
            if fn.lower().endswith(exts):
                out.append(os.path.join(dirpath, fn))
    return sorted(out)

def write_csv(path: str, rows: list[Dict[str, Any]], fieldnames: list[str]) -> None:
    ensure_dir(os.path.dirname(path))
    with open(path, "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        for r in rows:
            w.writerow(r)

def copy_if_missing(src: str, dst: str) -> bool:
    if os.path.exists(dst):
        return False
    ensure_dir(os.path.dirname(dst))
    shutil.copy2(src, dst)
    return True

def log(msg: str) -> None:
    print(msg, flush=True)

def env_run_id() -> str:
    rid = os.environ.get("RUN_ID")
    if not rid:
        rid = timestamp()
        os.environ["RUN_ID"] = rid
    return rid
