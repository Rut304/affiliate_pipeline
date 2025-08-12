# validate_narration_schema.py
import os

def validate_narration_schema(folder="narration", min_length=50, required_phrases=None, auto_fix=True):
    if required_phrases is None:
        required_phrases = ["Introducing", "Experience"]

    issues = []
    fixed = 0

    for filename in os.listdir(folder):
        if not filename.lower().endswith(".txt"):
            continue

        path = os.path.join(folder, filename)
        with open(path, "r") as f:
            content = f.read().strip()

        basename = os.path.splitext(filename)[0]
        has_placeholder = "[Narration placeholder" in content
        too_short = len(content) < min_length
        missing_phrases = [p for p in required_phrases if p not in content]

        if has_placeholder or too_short or missing_phrases:
            issues.append(f"⚠️ {filename} failed schema check.")

            if auto_fix:
                new_content = (
                    f"Introducing {basename} — a versatile product designed for modern needs. "
                    f"Experience the perfect blend of innovation and simplicity."
                )
                with open(path, "w") as f:
                    f.write(new_content)
                fixed += 1

    if not issues:
        return "✅ All narration files passed schema validation."
    
    msg = "\n".join(issues)
    if auto_fix:
        msg += f"\n🛠️ Auto-fixed {fixed} file(s) with generic narration."
    return msg

if __name__ == "__main__":
    print(validate_narration_schema())
