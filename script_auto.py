# script_auto.py
import argparse, json, random, re
from pathlib import Path
from typing import Dict, List

TEMPLATES = {
    "persuasive": (
        "{hook}\n\n"
        "Meet the {title} — built to make your day easier.\n"
        "Top features: {features}.\n"
        "Why it matters: {benefits}.\n\n"
        "[CTA_PRIMARY]\n"
    ),
    "casual": (
        "{hook}\n\n"
        "This is the {title}. It’s simple, solid, and just works.\n"
        "What you get: {features}.\n"
        "Nice perks: {benefits}.\n\n"
        "[CTA_PRIMARY]\n"
    ),
    "urgent": (
        "{hook}\n\n"
        "Grab the {title} while it’s in stock.\n"
        "Key features: {features}.\n"
        "Big wins: {benefits}.\n\n"
        "[CTA_PRIMARY]\n"
    ),
}

HOOKS = {
    "persuasive": [
        "Level up your daily routine in under a minute.",
        "Small upgrade, outsized results.",
        "Stop settling — make the jump."
    ],
    "casual": [
        "Quick share — this one’s worth a look.",
        "If you like things that just work, you’ll like this.",
        "Here’s a neat upgrade with zero fuss."
    ],
    "urgent": [
        "Don’t wait on this — you’ll use it every day.",
        "Limited stock. Big utility. Easy win.",
        "If you’ve been on the fence, this is your nudge."
    ],
}

def slugify(s: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", s.lower()).strip("-")

def list_to_phrase(items: List[str]) -> str:
    items = [i.strip() for i in items if i and i.strip()]
    if not items: return ""
    if len(items) == 1: return items[0]
    return ", ".join(items[:-1]) + " and " + items[-1]

def render_narration(meta: Dict, tone: str, rng: random.Random) -> str:
    title = meta.get("title", "").strip()
    features = list_to_phrase(meta.get("features", []))
    benefits = list_to_phrase(meta.get("benefits", []))
    tmpl = TEMPLATES.get(tone, TEMPLATES["persuasive"])
    hook = rng.choice(HOOKS.get(tone, HOOKS["persuasive"]))
    narration = tmpl.format(title=title, features=features, benefits=benefits, hook=hook).strip() + "\n"
    return narration

def generate_for_pack(pack_dir: Path, out_dir: Path, tone_override: str, rng: random.Random, force: bool, max_words: int) -> Path:
    pack_json = pack_dir / "product_pack.json"
    if not pack_json.exists():
        print(f"[skip] No product_pack.json in {pack_dir}")
        return None
    meta = json.loads(pack_json.read_text())
    product_id = meta.get("id") or pack_dir.name
    product_id = slugify(product_id)
    tone = tone_override or meta.get("tone") or "persuasive"

    out_dir.mkdir(parents=True, exist_ok=True)
    out_file = out_dir / f"{product_id}.txt"
    if out_file.exists() and not force:
        print(f"[keep] {out_file.name} exists (use --force to regenerate)")
        return out_file

    narration = render_narration(meta, tone, rng)

    # Word cap if requested (soft truncate by sentences)
    if max_words > 0:
        words = narration.split()
        if len(words) > max_words:
            narration = " ".join(words[:max_words])
            if not narration.endswith((".", "!", "?")):
                narration += "…"
            narration += "\n"

    out_file.write_text(narration)
    print(f"[write] {out_file} ({len(narration.split())} words, tone={tone})")
    return out_file

def main():
    p = argparse.ArgumentParser(description="Batch narration generator")
    p.add_argument("--source", default="packs", help="Root folder of product packs")
    p.add_argument("--output", default="narration", help="Output folder for narration files")
    p.add_argument("--tone", default=None, help="Override tone for all (persuasive|casual|urgent)")
    p.add_argument("--force", action="store_true", help="Overwrite existing narration files")
    p.add_argument("--seed", type=int, default=42, help="Random seed for deterministic hooks")
    p.add_argument("--max-words", type=int, default=0, help="Soft cap on word count (0=off)")
    args = p.parse_args()

    rng = random.Random(args.seed)
    src = Path(args.source)
    out = Path(args.output)

    if not src.exists():
        raise SystemExit(f"Source folder not found: {src}")

    packs = sorted([p for p in src.glob("*") if p.is_dir()])
    if not packs:
        print(f"[info] No packs found in {src}")
        return

    for pack in packs:
        generate_for_pack(pack, out, args.tone, rng, args.force, args.max_words)

if __name__ == "__main__":
    main()
