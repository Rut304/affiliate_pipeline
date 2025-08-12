import os

import requests
from dotenv import load_dotenv

load_dotenv()
key = os.getenv("SEGMIND_API_KEY")
print("🔑 Loaded key:", key)

headers = {"Authorization": f"Bearer {key}"}
response = requests.get("https://api.segmind.com/v1/pixelflow", headers=headers)
print("📡 Status code:", response.status_code)
print("📄 Response:", response.text)
