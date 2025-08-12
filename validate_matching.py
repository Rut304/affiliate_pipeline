# validate_matching.py
import os


def validate_matching(
    images_folder="images",
    narration_folder="narration",
    auto_stub=True,
    auto_cleanup=True,
):
    image_files = [
        f
        for f in os.listdir(images_folder)
        if f.lower().endswith((".jpg", ".png", ".jpeg"))
    ]
    narration_files = [
        f for f in os.listdir(narration_folder) if f.lower().endswith(".txt")
    ]

    image_basenames = {os.path.splitext(f)[0] for f in image_files}
    narration_basenames = {os.path.splitext(f)[0] for f in narration_files}

    missing_narration = image_basenames - narration_basenames
    extra_narration = narration_basenames - image_basenames

    messages = []

    if missing_narration:
        messages.append(
            f"⚠️ Missing narration for: {', '.join(sorted(missing_narration))}"
        )
        if auto_stub:
            for name in missing_narration:
                stub_path = os.path.join(narration_folder, f"{name}.txt")
                with open(stub_path, "w") as f:
                    f.write(f"[Narration placeholder for {name}]")
            messages.append(
                f"📝 Auto-generated {len(missing_narration)} narration stub(s)."
            )

    if extra_narration:
        messages.append(
            f"⚠️ Narration without matching image: {', '.join(sorted(extra_narration))}"
        )
        if auto_cleanup:
            for name in extra_narration:
                path = os.path.join(narration_folder, f"{name}.txt")
                os.remove(path)
            messages.append(
                f"🗑️ Deleted {len(extra_narration)} unmatched narration file(s)."
            )

    if not missing_narration and not extra_narration:
        messages.append("✅ All image and narration files are matched.")

    return "\n".join(messages)


if __name__ == "__main__":
    print(validate_matching())
