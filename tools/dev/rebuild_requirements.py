import ast
import os
import re
import sys

ROOT = os.getcwd()
SKIP_DIRS = {".git", ".venv", "out", "logs", "reports", "__pycache__"}

# Map import names -> pip package names
MAP = {
    # Core from earlier stages
    "yaml": "PyYAML",
    "PIL": "Pillow",
    "requests": "requests",
    "dotenv": "python-dotenv",
    "gtts": "gTTS",
    "pydub": "pydub",
    "validators": "validators",
    "mutagen": "mutagen",
    # Common video + data
    "moviepy": "moviepy",
    "imageio": "imageio",
    "numpy": "numpy",
    "pandas": "pandas",
    "tqdm": "tqdm",
    # Cloud / APIs often seen
    "boto3": "boto3",
    "botocore": "boto3",
    "google": "google-api-python-client",
    "googleapiclient": "google-api-python-client",
    # Media / cv
    "cv2": "opencv-python",
    "ffmpeg": "ffmpeg-python",
    # Tokenization / LLM utils (if present)
    "tiktoken": "tiktoken",
    # If you used a direct SDK
    "segmind": "segmind",
}

found = set()
unknown = set()


def add(name):
    base = name.split(".")[0]
    pkg = MAP.get(base)
    if pkg:
        found.add(pkg)
    else:
        # Heuristic: some imports are the pip name already
        if re.match(r"^[a-zA-Z0-9_\-]+$", base):
            unknown.add(base)


for dirpath, dirnames, filenames in os.walk(ROOT):
    dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS and not d.startswith(".")]
    for fn in filenames:
        if not fn.endswith(".py"):
            continue
        fp = os.path.join(dirpath, fn)
        try:
            with open(fp, "r", encoding="utf-8") as f:
                tree = ast.parse(f.read(), filename=fp)
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for n in node.names:
                        add(n.name)
                elif isinstance(node, ast.ImportFrom) and node.module:
                    add(node.module)
        except Exception:
            pass

# Cull obviously stdlib-ish names
STDLIB_HINTS = {
    "os",
    "sys",
    "json",
    "time",
    "re",
    "subprocess",
    "pathlib",
    "typing",
    "dataclasses",
    "logging",
    "argparse",
    "shutil",
    "itertools",
    "functools",
    "collections",
    "math",
    "random",
    "uuid",
    "csv",
    "glob",
    "tempfile",
    "hashlib",
    "base64",
    "http",
    "urllib",
    "html",
    "email",
    "unittest",
    "concurrent",
    "asyncio",
    "inspect",
}
unknown = {u for u in unknown if u not in STDLIB_HINTS}

# Print sorted requirements
for pkg in sorted(found):
    print(pkg)

# Emit any unknowns as a hint to stderr (so they don’t pollute stdout)
if unknown:
    sys.stderr.write("UNKNOWN_IMPORTS " + " ".join(sorted(unknown)) + "\n")
