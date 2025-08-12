# Load environment variables from .env
from dotenv import load_dotenv
import os

load_dotenv()

# Fetch Amazon credentials
ACCESS_KEY = os.getenv("AMAZON_ACCESS_KEY")
SECRET_KEY = os.getenv("AMAZON_SECRET_KEY")
TAG = os.getenv("AMAZON_ASSOCIATE_TAG")

# Optional: Debug print to confirm loading
print(f"✅ Loaded Amazon credentials: TAG={TAG}")

#!/usr/bin/env python3
import argparse
import json
import os
import sys
from pathlib import Path
from typing import List, Optional

import requests
from PIL import Image, ImageDraw, ImageFont
from dotenv import load_dotenv

# Optional: amazon-paapi imports guarded so placeholders still work without creds
try:
    from amazon_paapi import AmazonApi, AmazonApiException
except Exception:
    AmazonApi = None
    AmazonApiException = Exception

ROOT = Path(__file__).resolve().parents[1]  # repo root
CONTENT_DIR = ROOT / "content"

def load_json(p: Path) -> dict:
    with p.open("r", encoding="utf-8") as f:
        return json.load(f)

def dump_json(p: Path, data: dict) -> None:
    p.parent.mkdir(parents=True, exist_ok=True)
    with p.open("w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

def ensure_dir(p: Path) -> None:
    p.mkdir(parents=True, exist_ok=True)

def log(msg: str, level: str = "INFO", verbose: bool = True) -> None:
    if verbose:
        print(f"{level}: {msg}")

def get_target_packs(only: Optional[List[str]]) -> List[Path]:
    packs = []
    for p in sorted(CONTENT_DIR.glob("*")):
        if not p.is_dir():
            continue
        if only and p.name not in only:
            continue
        if not (p / "metadata.json").exists():
            continue
        packs.append(p)
    return packs

def init_amazon_api(verbose: bool = True):
    if AmazonApi is None:
        return None
    load_dotenv()
    partner_tag = os.getenv("AMAZON_PARTNER_TAG")
    access_key = os.getenv("AMAZON_ACCESS_KEY")
    secret_key = os.getenv("AMAZON_SECRET_KEY")
    if not all([partner_tag, access_key, secret_key]):
        return None
    try:
        api = AmazonApi(access_key, secret_key, partner_tag, country="US")
        return api
    except Exception as e:
        log(f"Amazon API init failed: {e}", "WARNING", verbose)
        return None

def country_from_marketplace(marketplace: str) -> str:
    mapping = {
        "US": "US", "CA": "CA", "UK": "UK", "GB": "UK",
        "DE": "DE", "FR": "FR", "IT": "IT", "ES": "ES",
        "JP": "JP", "AU": "AU", "IN": "IN", "BR": "BR", "MX": "MX"
    }
    return mapping.get(marketplace.upper(), "US")

def fetch_amazon_image_urls(api, asin: Optional[str], keywords: Optional[str], marketplace: str, count: int, verbose: bool) -> List[str]:
    if api is None:
        return []
    # reconfigure region if needed
    try:
        api.country = country_from_marketplace(marketplace or "US")
    except Exception:
        pass
    urls: List[str] = []
    try:
        if asin:
            items = api.get_items([asin])
            for it in items.items:
                imgs = []
                # Primary first
                if it.images and it.images.large:
                    imgs.append(it.images.large.url)
                # Variants
                if it.images and it.images.variants:
                    for v in it.images.variants:
                        if v.large and v.large.url:
                            imgs.append(v.large.url)
                urls.extend(imgs)
        elif keywords:
            results = api.search_items(keywords=keywords, item_count=min(10, count*2))
            for it in results.items:
                if it.images and it.images.large:
                    urls.append(it.images.large.url)
        # Deduplicate and limit
        dedup = []
        for u in urls:
            if u and u not in dedup:
                dedup.append(u)
        urls = dedup[:count]
        return urls
    except AmazonApiException as e:
        log(f"Amazon API error: {e}", "WARNING", verbose)
        return []
    except Exception as e:
        log(f"Amazon fetch error: {e}", "WARNING", verbose)
        return []

def download_images(urls: List[str], out_dir: Path, verbose: bool) -> List[str]:
    saved = []
    ensure_dir(out_dir)
    for idx, url in enumerate(urls, start=1):
        try:
            r = requests.get(url, timeout=15)
            r.raise_for_status()
            ext = ".jpg"
            if "image/png" in r.headers.get("Content-Type", "") or url.lower().endswith(".png"):
                ext = ".png"
            fname = f"img{idx}{ext}"
            fpath = out_dir / fname
            with open(fpath, "wb") as f:
                f.write(r.content)
            saved.append(fname)
            log(f"Downloaded: {fname}", "DEBUG", verbose)
        except Exception as e:
            log(f"Download failed for {url}: {e}", "WARNING", verbose)
    return saved

def generate_placeholder(out_dir: Path, name: str, text: str, theme: str, size=(1280, 720)) -> str:
    ensure_dir(out_dir)
    img = Image.new("RGB", size, color=(28, 30, 34))  # dark bg
    draw = ImageDraw.Draw(img)
    try:
        font = ImageFont.truetype("Arial.ttf", 42)
    except Exception:
        font = ImageFont.load_default()
    title = text[:42] + ("..." if len(text) > 42 else "")
    sub = f"{theme or 'generic'} placeholder"
    W, H = img.size
    tw, th = draw.textlength(title, font=font), 42
    sw, sh = draw.textlength(sub, font=font), 42
    draw.text(((W - tw)/2, H/2 - th), title, fill=(235, 235, 235), font=font)
    draw.text(((W - sw)/2, H/2 + 10), sub, fill=(180, 180, 180), font=font)
    fname = f"{name}.jpg"
    img.save(out_dir / fname, format="JPEG", quality=90)
    return fname

def ensure_image_count(pack_dir: Path, needed: int, theme: str, title: str, verbose: bool) -> List[str]:
    images_dir = pack_dir / "images"
    ensure_dir(images_dir)
    existing = sorted([p.name for p in images_dir.iterdir() if p.is_file() and p.suffix.lower() in (".jpg", ".jpeg", ".png")])
    have = len(existing)
    if have >= needed:
        return existing[:needed]
    # Generate placeholders for the remainder
    remain = needed - have
    log(f"Filling {remain} placeholders", "INFO", verbose)
    added = []
    for i in range(1, remain + 1):
        name = f"img{have + i}"
        fname = generate_placeholder(images_dir, name=name, text=title or "Product", theme=theme or "generic")
        added.append(fname)
    return sorted([*existing, *added])[:needed]

def process_pack(pack_dir: Path, api, dry_run: bool, verbose: bool) -> dict:
    meta_path = pack_dir / "metadata.json"
    meta = load_json(meta_path)
    title = meta.get("title", pack_dir.name)
    theme = meta.get("theme", "generic")
    image_count = int(meta.get("image_count", 5))
    policy = meta.get("image_policy", "auto")
    product = meta.get("product", {}) or {}

    out_dir = pack_dir / "images"
    ensure_dir(out_dir)

    result = {"pack": pack_dir.name, "requested": image_count, "downloaded": [], "placeholders": [], "status": "ok"}

    if policy != "auto":
        log(f"{pack_dir.name}: image_policy != auto; skipping fetch", "INFO", verbose)
        final = ensure_image_count(pack_dir, image_count, theme, title, verbose)
        result["placeholders"] = final
        return result

    asin = product.get("asin")
    marketplace = product.get("marketplace", "US")
    keywords = product.get("keywords")

    urls = fetch_amazon_image_urls(api, asin=asin, keywords=keywords, marketplace=marketplace, count=image_count, verbose=verbose)
    if urls:
        log(f"{pack_dir.name}: Amazon returned {len(urls)} urls", "INFO", verbose)
        if not dry_run:
            downloaded = download_images(urls, out_dir, verbose)
            result["downloaded"] = downloaded
        else:
            result["downloaded"] = [f"img{i+1}.jpg" for i in range(len(urls))]
    else:
        log(f"{pack_dir.name}: No Amazon images found; will fill with placeholders", "WARNING", verbose)

    # Top up to image_count with placeholders
    final_images = ensure_image_count(pack_dir, image_count, theme, title, verbose)
    result["placeholders"] = [img for img in final_images if img not in result["downloaded"]]
    # Write manifest for traceability
    if not dry_run:
        manifest = {
            "source": "amazon" if urls else "placeholder",
            "downloaded": result["downloaded"],
            "placeholders": result["placeholders"]
        }
        dump_json(pack_dir / "images_manifest.json", manifest)
    return result

def main():
    parser = argparse.ArgumentParser(description="Auto-fetch images for affiliate packs (Amazon + placeholders).")
    parser.add_argument("--only", nargs="*", help="Pack folder names (e.g., 003_affiliate_airfryer)")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--verbose", action="store_true")
    args = parser.parse_args()

    packs = get_target_packs(args.only)
    if not packs:
        print("No packs found. Check content/* and --only filters.")
        sys.exit(1)

    api = init_amazon_api(verbose=args.verbose)

    summary = []
    for p in packs:
        res = process_pack(p, api=api, dry_run=args.dry_run, verbose=args.verbose)
        summary.append(res)

    print("\n=== Image Fetch Summary ===")
    for s in summary:
        print(f"{s['pack']}: requested={s['requested']} downloaded={len(s['downloaded'])} placeholders={len(s['placeholders'])} status={s['status']}")

if __name__ == "__main__":
    main()
