import os
import sys
import requests

ACCOUNT_URL = "https://api.segmind.com/v1/account"
WORKFLOW_URL = os.getenv(
    "SEGMIND_WORKFLOW_URL",
    "https://api.segmind.com/workflows/<your_workflow_id>-v1"
)

def _headers():
    api_key = os.getenv("SEGMIND_API_KEY", "").strip()
    if not api_key or len(api_key) < 25:
        sys.exit("[ERROR] SEGMIND_API_KEY missing or too short — regenerate a full key in Segmind dashboard.")
    return {"x-api-key": api_key, "Content-Type": "application/json"}

def check_account():
    print(f"[TEST] GET {ACCOUNT_URL}")
    r = requests.get(ACCOUNT_URL, headers={"x-api-key": _headers()["x-api-key"]}, timeout=20)
    if r.status_code != 200:
        sys.exit(f"[FAIL] /account: {r.status_code} {r.text.strip()}")
    print("[OK] Segmind account auth passed.")

def check_workflow():
    print(f"[TEST] POST {WORKFLOW_URL} (empty JSON payload)")
    r = requests.post(WORKFLOW_URL, headers=_headers(), json={}, timeout=30)
    if r.status_code in (401, 403):
        sys.exit(f"[FAIL] Workflow auth denied: {r.status_code} {r.text.strip()}")
    if r.status_code in (404, 405):
        sys.exit(f"[FAIL] Workflow URL invalid or not live: {r.status_code} {r.text.strip()}")
    print(f"[OK] Workflow endpoint reachable: {r.status_code}")

def main():
    check_account()
    check_workflow()
    print("[DONE] Segmind auth & endpoint sanity checks passed.")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n[ABORTED] Interrupted by user.")
        sys.exit(130)
