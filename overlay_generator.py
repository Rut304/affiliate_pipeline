# overlay_generator.py
import argparse
import json
from pathlib import Path

WORDS_PER_MIN = 165.0
MIN_DURATION_SEC = 6.0
CTA_WINDOW_FRACTION = 0.25  # CTA shows for last 25% of estimated duration
OUT_DIR_DEFAULT = "overlays"

STYLE_PRESETS = {
    "dark_glow": {
        "font_family": "Inter-SemiBold",
        "font_size": 42,
        "text_color": "#FFFFFF",
        "shadow": {"color": "#000000", "blur": 12, "opacity": 0.65},
        "button": {
            "bg_color": "#FF7A00",
            "text_color": "#FFFFFF",
            "font_family": "Inter-Bold",
            "font_size": 32,
            "radius": 12,
            "padding": [18, 28],
        },
    },
    "light_elevated": {
        "font_family": "Inter-SemiBold",
        "font_size": 42,
        "text_color": "#111111",
        "shadow": {"color": "#000000", "blur": 10, "opacity": 0.25},
        "button": {
            "bg_color": "#111111",
            "text_color": "#FFFFFF",
            "font_family": "Inter-Bold",
            "font_size": 32,
            "radius": 12,
            "padding": [18, 28],
        },
    },
}


def estimate_duration_sec(text: str) -> float:
    words = max(1, len(text.strip().split()))
    est = (words / WORDS_PER_MIN) * 60.0
    return max(MIN_DURATION_SEC, round(est, 2))


def cta_timing(total_sec: float) -> tuple[float, float]:
    # CTA shows in the last 25% of narration, min 3s window, clamps to total length
    window = max(3.0, round(total_sec * CTA_WINDOW_FRACTION, 2))
    start = max(0.0, round(total_sec - window, 2))
    end = round(total_sec, 2)
    return start, end


def style_preset(name: str) -> dict:
    return STYLE_PRESETS.get(name, STYLE_PRESETS["dark_glow"])


def build_overlay_spec(narration_text: str, source_path: Path, style_name: str) -> dict:
    total = estimate_duration_sec(narration_text)
    start, end = cta_timing(total)
    s = style_preset(style_name)
    stem = source_path.stem

    return {
        "id": stem,
        "source": str(source_path),
        "estimated_duration_sec": total,
        "style": s,
        "safe_area": {"margin": 0.06},  # 6% margins
        "overlays": [
            {
                "type": "cta",
                "text_placeholder": "[CTA_PRIMARY]",
                "url_placeholder": "[AFFILIATE_URL]",
                "start": start,
                "end": end,
                "position": {
                    "anchor": "bottom_center",
                    "x": 0.5,  # normalized
                    "y": 0.90,  # 90% height
                    "max_width": 0.86,  # normalized width
                },
                "button": {"align": "center", "icon": "external_link"},
            }
        ],
        "meta": {
            "generator": "overlay_generator.py",
            "version": 1,
            "style_name": style_name,
        },
    }


def generate_overlays(
    narration_dir: str, out_dir: str, style_name: str, require_cta=True
) -> list[Path]:
    n_dir = Path(narration_dir)
    o_dir = Path(out_dir)
    if not n_dir.exists():
        raise FileNotFoundError(f"Narration directory not found: {n_dir}")
    o_dir.mkdir(parents=True, exist_ok=True)

    written = []
    for txt in sorted(n_dir.glob("*.txt")):
        text = txt.read_text().strip()
        if require_cta and "[CTA_PRIMARY]" not in text:
            print(
                f"[skip] {txt.name}: missing [CTA_PRIMARY] (preflight should prevent this)"
            )
            continue

        spec = build_overlay_spec(text, txt, style_name)
        out_path = o_dir / f"{txt.stem}.json"
        out_path.write_text(json.dumps(spec, indent=2))
        print(f"[write] {out_path} ({len(text.split())} words)")
        written.append(out_path)
    return written


def main():
    ap = argparse.ArgumentParser(
        description="Generate overlay JSON specs from narration files."
    )
    ap.add_argument("--narration-dir", default="narration")
    ap.add_argument("--out", default=OUT_DIR_DEFAULT)
    ap.add_argument("--style", default="dark_glow", choices=list(STYLE_PRESETS.keys()))
    ap.add_argument(
        "--allow-missing-cta",
        action="store_true",
        help="Generate specs even if CTA placeholder is missing",
    )
    args = ap.parse_args()

    generate_overlays(
        narration_dir=args.narration_dir,
        out_dir=args.out,
        style_name=args.style,
        require_cta=not args.allow_missing_cta,
    )


if __name__ == "__main__":
    main()
