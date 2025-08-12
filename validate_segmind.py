# validate_segmind.py
import os
from dotenv import load_dotenv
import requests

def validate_segmind():
    load_dotenv()
    key = os.getenv("SEGMIND_API_KEY")

    if not key or len(key) < 30:
        return "❌ Segmind API key missing or malformed."

    headers = {"Authorization": f"Bearer {key}"}
    url = "https://api.segmind.com/v1/pixelflow"
    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        return "✅ Segmind API access confirmed."
    elif response.status_code == 401:
        return "❌ Unauthorized. Check key or plan access."
    elif response.status_code == 404:
        return "⚠️ Endpoint not found. Double-check URL."
    else:
        return f"❌ Unexpected error: {response.status_code}"

if __name__ == "__main__":
    print(validate_segmind())
