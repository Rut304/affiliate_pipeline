# resolve_links.py
from pathlib import Path

import yaml


def load_yaml(path):
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def write_yaml(data, path):
    with open(path, "w", encoding="utf-8") as f:
        yaml.dump(data, f, allow_unicode=True, sort_keys=False)


def resolve_links(pack_id):
    base_dir = Path("content") / pack_id
    input_path = base_dir / "input.yaml"
    affiliate_path = Path("affiliate_links.yaml")

    data = load_yaml(input_path)
    links = load_yaml(affiliate_path)
    updated = 0

    for product in data.get("products", []):
        asin = product.get("asin")
        if asin and "link" not in product:
            link = links.get(asin)
            if link:
                product["link"] = link
                print(f"🔗 Added link for {asin}: {link}")
                updated += 1
            else:
                print(f"⚠️ No link found for {asin}")

    write_yaml(data, input_path)
    print(f"✅ Injected {updated} affiliate link(s) into {pack_id}/input.yaml")


if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("Usage: python resolve_links.py <pack_id>")
        sys.exit(1)
    resolve_links(sys.argv[1])
