# validate_images.py
import os

def validate_images(folder="images"):
    if not os.path.isdir(folder):
        return f"❌ Image folder '{folder}' not found."

    files = [f for f in os.listdir(folder) if f.lower().endswith((".png", ".jpg", ".jpeg"))]
    if not files:
        return f"⚠️ No valid image files found in '{folder}'."
    
    return f"✅ Found {len(files)} image(s) in '{folder}'."

if __name__ == "__main__":
    print(validate_images())
