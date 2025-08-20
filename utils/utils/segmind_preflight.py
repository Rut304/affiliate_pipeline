import os
import sys
import requests

ACCOUNT_URL = "https://api.segmind.com/v1/account"
WORKFLOW_URL = "https://api.segmind.com/workflows/689e3459c49c91c2edbbb0c1-v1"

def check_auth():
    api_key = os.getenv("SEGMIND_API_KEY", "").strip()
    if not api_key or len(api_key) < 25:
        sys.exit("[ERROR] SEGMIND_API_KEY missing or too short — regenerate it in Segmind dashboard.")

    headers = {"Authorization": f"Bearer {api_key}"}

    # 1️⃣ Check /account
    r = requests.get(ACCOUNT_URL, headers=headers)
    if r.status_code != 200:
        sys.exit(f"[ERROR] Segmind /account check failed: {r.status_code} {r.text.strip()}")
    print("[OK] Segmind account check passed.")

    # 2️⃣ Check workflow endpoint — dry run with minimal payload
    payload = {
        "your_input_name": "test"  # Replace with real API input param name
    }
    r = requests.post(WORKFLOW_URL, headers={**headers, "Content-Type": "application/json"}, json=payload)
    if r.status_code not in (200, 202):
        sys.exit(f"[ERROR] Workflow endpoint check failed: {r.status_code} {r.text.strip()}")

    print("[OK] Workflow endpoint check passed.")

if __name__ == "__main__":
    check_auth()
