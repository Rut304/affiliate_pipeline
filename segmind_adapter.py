import os
import requests
from tqdm import tqdm

SEGMIND_API_KEY = os.getenv("SEGMIND_API_KEY", "SG_1da1828b99ada0e6")
SEGMIND_ENDPOINT = "https://api.segmind.com/v1/pixelflow"

def generate_product_video(image_path, prompt, output_path):
    if not os.path.exists(image_path):
        raise FileNotFoundError(f"Image not found: {image_path}")

    with open(image_path, "rb") as img_file:
        files = {"image": img_file}
        data = {"prompt": prompt}
        headers = {"Authorization": f"Bearer {SEGMIND_API_KEY}"}

        print(f"📤 Sending image to Segmind: {image_path}")
        response = requests.post(SEGMIND_ENDPOINT, headers=headers, files=files, data=data)
        response.raise_for_status()

        video_url = response.json().get("video_url")
        if not video_url:
            raise ValueError("No video URL returned from Segmind")

        print(f"📥 Downloading video from: {video_url}")
        video_response = requests.get(video_url, stream=True)
        video_response.raise_for_status()

        with open(output_path, "wb") as f:
            for chunk in tqdm(video_response.iter_content(chunk_size=8192), desc="Saving video"):
                f.write(chunk)

        print(f"✅ Video saved to: {output_path}")
