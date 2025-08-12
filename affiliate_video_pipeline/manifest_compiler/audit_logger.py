import os
from datetime import datetime

LOG_DIR = "logs"
os.makedirs(LOG_DIR, exist_ok=True)

def log_pipeline_run(summary: str, details: list[str]):
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    log_path = os.path.join(LOG_DIR, f"run_{timestamp}.log")
    with open(log_path, "w") as f:
        f.write(f"[{timestamp}] {summary}\n\n")
        for line in details:
            f.write(f"{line}\n")
    print(f"📝 Audit log saved: {log_path}")
