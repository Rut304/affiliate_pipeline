import os

import yaml
from PIL import Image, ImageDraw


def generate_images(pack_id):
    input_path = f"content/{pack_id}/input.yaml"
    output_dir = f"content/{pack_id}/images"
    os.makedirs(output_dir, exist_ok=True)

    with open(input_path, "r") as f:
        data = yaml.safe_load(f)

    for product in data["products"]:
        img_path = os.path.join(output_dir, product["image"])
        title = product.get("title", product["asin"])

        img = Image.new("RGB", (512, 512), color="white")
        draw = ImageDraw.Draw(img)

        # Optional: Customize font size and layout
        draw.text((20, 220), title, fill="black")
        img.save(img_path)

        print(f"🖼️ Generated: {img_path}")


# 👇 Run for your current pack
generate_images("003_affiliate_airfryer")
