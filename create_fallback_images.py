import os
import yaml
from PIL import Image, ImageDraw, ImageFont

def slugify(name):
    return name.lower().replace(" ", "_").replace("-", "_")

def create_placeholder(text, path, size=(1024, 768)):
    img = Image.new("RGB", size, color=(200, 200, 220))
    draw = ImageDraw.Draw(img)

    try:
        font = ImageFont.truetype("Arial.ttf", 36)
    except:
        font = ImageFont.load_default()

    draw.text((50, 50), text, fill="black", font=font)
    img.save(path)
    print(f"🖼️ Created {path}")

def generate_images(pack_id):
    input_file = f"content/{pack_id}/input.yaml"
    image_dir = f"content/{pack_id}/images"
    os.makedirs(image_dir, exist_ok=True)

    if not os.path.exists(input_file):
        print(f"⚠️ Missing input.yaml for pack '{pack_id}'")
        return

    with open(input_file) as f:
        data = yaml.safe_load(f)
    
    products = data.get("products", [])
    if not products:
        print(f"⚠️ No products found in {input_file}")
        return

    for product in products:
        name = product.get("name", "Unnamed Product")
        filename = f"{slugify(name)}.jpg"
        out_path = os.path.join(image_dir, filename)

        if not os.path.exists(out_path):
            create_placeholder(name, out_path)
        else:
            print(f"⏩ Skipped (exists): {filename}")

if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("Usage: python create_fallback_images.py <pack_id>")
    else:
        generate_images(sys.argv[1])
