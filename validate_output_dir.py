# validate_output_dir.py
import os


def validate_output_dir(folder="output"):
    if not os.path.exists(folder):
        try:
            os.makedirs(folder)
            return f"✅ Output folder '{folder}' created."
        except Exception as e:
            return f"❌ Failed to create output folder: {e}"
    return f"✅ Output folder '{folder}' is ready."


if __name__ == "__main__":
    print(validate_output_dir())
