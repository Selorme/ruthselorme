import os
from PIL import Image

# Folder where your images are located
IMAGE_DIR = "static/img"
VALID_EXTENSIONS = (".png", ".jpg", ".jpeg")


def convert_to_webp(image_dir):
    for root, dirs, files in os.walk(image_dir):
        for file in files:
            if file.lower().endswith(VALID_EXTENSIONS):
                source_path = os.path.join(root, file)
                webp_path = os.path.splitext(source_path)[0] + ".webp"

                if os.path.exists(webp_path):
                    print(f"⚠️ Already exists: {webp_path}")
                    continue

                try:
                    img = Image.open(source_path)

                    # If image has transparency, keep it with RGBA; otherwise, use RGB
                    if img.mode in ("RGBA", "LA") or (img.mode == "P" and "transparency" in img.info):
                        img = img.convert("RGBA")
                    else:
                        img = img.convert("RGB")

                    img.save(webp_path, "webp", quality=85, lossless=True)
                    print(f"✅ Converted: {source_path} → {webp_path}")
                except Exception as e:
                    print(f"❌ Failed to convert {source_path}: {e}")


if __name__ == "__main__":
    convert_to_webp(IMAGE_DIR)
