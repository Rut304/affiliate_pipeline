# generate_dummy_narration.py
narrations = {
    "product1.txt": "Introducing Product 1 — a sleek, modern solution for your everyday needs. Designed with precision and built to last.",
    "product2.txt": "Product 2 brings innovation to your fingertips. Experience the future of convenience and style in one compact package.",
}

for filename, content in narrations.items():
    with open(f"narration/{filename}", "w") as f:
        f.write(content)
