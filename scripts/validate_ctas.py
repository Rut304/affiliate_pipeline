#!/usr/bin/env python3
import os

from _utils import dump_yaml, env_run_id, list_packs, load_yaml, log, write_csv

PACKS_ROOT = "packs"
TEMPLATE_CTA = "templates/cta_primary.txt"
RUN_ID = env_run_id()


def read_template_cta() -> str | None:
    if os.path.isfile(TEMPLATE_CTA):
        with open(TEMPLATE_CTA, "r", encoding="utf-8") as f:
            return f.read().strip()
    return None


def main():
    packs = list_packs(PACKS_ROOT)
    cta_tpl = read_template_cta()
    rows = []
    for pack in packs:
        pack_name = os.path.basename(pack)
        input_yaml = os.path.join(pack, "input.yaml")
        input_found = os.path.isfile(input_yaml)
        before = ""
        after = ""
        changed = False
        note = ""
        if not input_found:
            note = "missing input.yaml"
        else:
            try:
                data = load_yaml(input_yaml)
                before = (
                    (data.get("cta_primary") or "") if isinstance(data, dict) else ""
                )
                if (not before) and cta_tpl:
                    data["cta_primary"] = cta_tpl
                    dump_yaml(input_yaml, data)
                    after = cta_tpl
                    changed = True
                    note = "patched from template"
                elif (not before) and not cta_tpl:
                    note = "cta missing; no template available"
                else:
                    after = before
                    note = "cta present; no change"
            except Exception as e:
                note = f"error: {e!s}"

        rows.append(
            {
                "run_id": RUN_ID,
                "pack": pack_name,
                "input_yaml_found": input_found,
                "cta_before": before,
                "cta_after": after,
                "changed": changed,
                "note": note,
            }
        )
        log(f"[{RUN_ID}] CTA | {pack_name} | {note}")

    out_csv = os.path.join("logs", f"run_{RUN_ID}", "validate_ctas.csv")
    write_csv(
        out_csv,
        rows,
        [
            "run_id",
            "pack",
            "input_yaml_found",
            "cta_before",
            "cta_after",
            "changed",
            "note",
        ],
    )


if __name__ == "__main__":
    main()
