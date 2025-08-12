# generate_cta_overlays.py
import argparse
from pathlib import Path

import yaml
from PIL import Image, ImageDraw, ImageFont

DEFAULT_TEXT = "Shop Now"
DEFAULT_TEXT_COLOR = "#FFFFFF"
DEFAULT_BAR_COLOR = "#000000"
DEFAULT_BAR_ALPHA = 170  # 0-255
DEFAULT_MARGIN = 24  # px padding inside bar
DEFAULT_BAR_HEIGHT_FRAC = 0.18  # 18% of height


def load_yaml(path: Path) -> dict:
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f) or {}


def find_font(size: int) -> ImageFont.FreeTypeFont:
    # Try a few common macOS/system fonts; fall back to default bitmap
    font_paths = [
        "/System/Library/Fonts/Supplemental/Arial Bold.ttf",
        "/System/Library/Fonts/Supplemental/Arial.ttf",
        "/System/Library/Fonts/Supplemental/Helvetica.ttf",
        "/System/Library/Fonts/Supplemental/HelveticaNeue.ttf",
    ]
    for p in font_paths:
        if Path(p).exists():
            try:
                return ImageFont.truetype(p, size=size)
            except Exception:
                continue
    return ImageFont.load_default()


def draw_cta(
    img: Image.Image,
    text: str,
    text_color: str,
    bar_color: str,
    bar_alpha: int,
    margin: int,
    bar_height_frac: float,
) -> Image.Image:
    w, h = img.size
    overlay = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)

    bar_h = max(48, int(h * bar_height_frac))
    bar_y0 = h - bar_h
    # Semi-transparent bar
    bc = ImageColor_getrgb_safe(bar_color)
    draw.rectangle([0, bar_y0, w, h], fill=(bc[0], bc[1], bc[2], bar_alpha))

    # Dynamic font sizing to fit width
    font_size = max(18, int(bar_h * 0.45))
    font = find_font(font_size)

    # Reduce font size until text fits inside bar with margins
    tw, th = draw.textbbox((0, 0), text, font=font)[2:]
    while (tw + 2 * margin > w) and font_size > 12:
        font_size -= 2
        font = find_font(font_size)
        tw, th = draw.textbbox((0, 0), text, font=font)[2:]

    tx = max(margin, (w - tw) // 2)
    ty = bar_y0 + (bar_h - th) // 2

    tc = ImageColor_getrgb_safe(text_color)
    draw.text((tx, ty), text, fill=(tc[0], tc[1], tc[2], 255), font=font)
    return Image.alpha_composite(img.convert("RGBA"), overlay)


def ImageColor_getrgb_safe(color_hex: str):
    # Simple hex -> RGB parser supporting #RRGGBB
    color_hex = color_hex.strip()
    if color_hex.startswith("#"):
        color_hex = color_hex[1:]
    if len(color_hex) != 6:
        return (255, 255, 255)
    return tuple(int(color_hex[i : i + 2], 16) for i in (0, 2, 4))


def process_pack(
    pack_id: str,
    text: str,
    text_color: str,
    bar_color: str,
    bar_alpha: int,
    margin: int,
    bar_height_frac: float,
    overwrite: bool,
):
    pack_dir = Path("content") / pack_id
    yaml_path = pack_dir / "input.yaml"
    data = load_yaml(yaml_path)
    products = data.get("products") or []

    src_dir = pack_dir / "images"
    out_dir = pack_dir / "images_cta"
    out_dir.mkdir(parents=True, exist_ok=True)

    created, skipped = 0, 0

    for product in products:
        image_name = product.get("image")
        if not image_name:
            continue
        src_path = src_dir / image_name
        if not src_path.exists():
            print(f"⚠️ Missing source image: {src_path}")
            continue

        dst_path = out_dir / image_name
        if dst_path.exists() and not overwrite:
            skipped += 1
            continue

        with Image.open(src_path) as im:
            out = draw_cta(
                im, text, text_color, bar_color, bar_alpha, margin, bar_height_frac
            )
            # Save as JPEG/PNG based on original extension
            params = {}
            if dst_path.suffix.lower() in [".jpg", ".jpeg"]:
                params["quality"] = 92
            out.convert("RGB").save(dst_path, **params)

        created += 1
        print(f"🏷️  CTA: {dst_path}")

    print(
        f"✅ Overlays done — created: {created}, skipped: {skipped}, total: {len(products)}"
    )


def main():
    ap = argparse.ArgumentParser(description="Generate CTA overlays for pack images.")
    ap.add_argument("pack_id", help="Pack under content/, e.g., 003_affiliate_airfryer")
    ap.add_argument(
        "--text", default=DEFAULT_TEXT, help='CTA text (default "Shop Now")'
    )
    ap.add_argument(
        "--text-color",
        default=DEFAULT_TEXT_COLOR,
        help="CTA text color hex (default #FFFFFF)",
    )
    ap.add_argument(
        "--bar-color", default=DEFAULT_BAR_COLOR, help="Bar color hex (default #000000)"
    )
    ap.add_argument(
        "--bar-alpha",
        type=int,
        default=DEFAULT_BAR_ALPHA,
        help="Bar opacity 0-255 (default 170)",
    )
    ap.add_argument(
        "--margin",
        type=int,
        default=DEFAULT_MARGIN,
        help="Inner padding in px (default 24)",
    )
    ap.add_argument(
        "--bar-height-frac",
        type=float,
        default=DEFAULT_BAR_HEIGHT_FRAC,
        help="Bar height fraction of image (default 0.18)",
    )
    ap.add_argument(
        "--overwrite", action="store_true", help="Overwrite existing outputs"
    )
    args = ap.parse_args()

    process_pack(
        args.pack_id,
        args.text,
        args.text_color,
        args.bar_color,
        args.bar_alpha,
        args.margin,
        args.bar_height_frac,
        args.overwrite,
    )


if __name__ == "__main__":
    main()
