# seed_images_from_template.py
import os
import yaml
import shutil

def slugify(name):
    return name.lower().replace(" ", "_").replace("-", "_")

def seed_images(pack_id, source_pool="content/003_affiliate_airfryer/images"):
    input_path = f"content/{pack_id}/input.yaml"
    image_dest = f"content/{pack_id}/images"
    
    os.makedirs(image_dest, exist_ok=True)

    with open(input_path) as f:
        data = yaml.safe_load(f)

    products = data.get("products", [])
    if not products:
        print(f"⚠️ No products found in {input_path}")
        return

    pool_images = sorted([
        os.path.join(source_pool, f) for f in os.listdir(source_pool)
        if f.lower().endswith(".jpg")
    ])

    if not pool_images:
        print(f"⚠️ No source images found in {source_pool}")
        return

    print(f"📦 Seeding {len(products)} images into {image_dest}")

    for i, product in enumerate(products):
        slug = slugify(product.get("name", f"product{i+1}"))
        target_path = os.path.join(image_dest, f"{slug}.jpg")
        source_img = pool_images[i % len(pool_images)]
        shutil.copy2(source_img, target_path)
        print(f"✅ {slug}.jpg ← {os.path.basename(source_img)}")

if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("Usage: python seed_images_from_template.py <pack_id>")
    else:
        seed_images(sys.argv[1])
