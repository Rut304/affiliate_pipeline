#!/usr/bin/env python3
import os, re
from _utils import list_packs, write_csv, env_run_id, log, ensure_dir, copy_if_missing

PACKS_ROOT = "packs"
RUN_ID = env_run_id()
IMG_EXTS = (".jpg", ".jpeg", ".png")
FALLBACK_NAME = "_default.jpg"
STEP_REGEX = re.compile(r"^(\d{1,3})")  # e.g., 01_intro.txt

def extract_step_index(filename: str, seq: int) -> str:
    m = STEP_REGEX.match(os.path.basename(filename))
    if m:
        return m.group(1).zfill(2)
    return str(seq).zfill(2)

def find_image_for_step(images_dir: str, step: str) -> str | None:
    for ext in IMG_EXTS:
        candidate = os.path.join(images_dir, f"{step}{ext}")
        if os.path.isfile(candidate):
            return candidate
    for fn in os.listdir(images_dir) if os.path.isdir(images_dir) else []:
        base, ext = os.path.splitext(fn)
        if ext.lower() in IMG_EXTS and (base == step or base.startswith(f"{step}_")):
            return os.path.join(images_dir, fn)
    return None

def main():
    packs = list_packs(PACKS_ROOT)
    summary_rows = []
    for pack in packs:
        pack_name = os.path.basename(pack)
        narr_dir = os.path.join(pack, "narration")
        img_dir = os.path.join(pack, "images")
        ensure_dir(img_dir)
        narration_txts = sorted([os.path.join(narr_dir, f) for f in os.listdir(narr_dir)]) if os.path.isdir(narr_dir) else []
        narration_txts = [p for p in narration_txts if p.lower().endswith(".txt")]
        fallback_src = os.path.join(img_dir, FALLBACK_NAME)
        created = matched = missing = 0
        mapping_rows = []

        for i, npath in enumerate(narration_txts, start=1):
            step = extract_step_index(npath, i)
            found = find_image_for_step(img_dir, step)
            out_img = ""
            is_fallback = False
            if found:
                matched += 1
                out_img = os.path.relpath(found, pack)
            else:
                missing += 1
                dst = os.path.join(img_dir, f"{step}_fallback.jpg")
                if os.path.isfile(fallback_src):
                    if copy_if_missing(fallback_src, dst):
                        created += 1
                        is_fallback = True
                        out_img = os.path.relpath(dst, pack)
                    else:
                        is_fallback = True
                        out_img = os.path.relpath(dst, pack)

            mapping_rows.append({
                "run_id": RUN_ID,
                "pack": pack_name,
                "step": step,
                "narration_txt": os.path.relpath(npath, pack),
                "image_path": out_img,
                "is_fallback": is_fallback,
                "had_image": bool(found)
            })

        map_csv = os.path.join(pack, "images_map.csv")
        write_csv(map_csv, mapping_rows, ["run_id","pack","step","narration_txt","image_path","is_fallback","had_image"])

        summary_rows.append({
            "run_id": RUN_ID,
            "pack": pack_name,
            "narration_count": len(narration_txts),
            "images_matched": matched,
            "fallbacks_created": created,
            "images_missing_after": sum(1 for r in mapping_rows if not r["image_path"])
        })
        log(f"[{RUN_ID}] IMG  | {pack_name} | matched={matched} fallback_created={created} missing={missing}")

    out_csv = os.path.join("logs", f"run_{RUN_ID}", "match_images.csv")
    write_csv(out_csv, summary_rows, ["run_id","pack","narration_count","images_matched","fallbacks_created","images_missing_after"])

if __name__ == "__main__":
    main()
