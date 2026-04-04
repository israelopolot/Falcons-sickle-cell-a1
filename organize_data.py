import os
import shutil
from pathlib import Path


def organize_sickle_data(source_dir="data/train/normal", sickle_dir="data/train/sickle"):
    """
    Helper script to manually organize images into normal vs sickle categories.

    Usage:
    1. Run download_kaggle_data.py first
    2. Images will be in data/train/normal/
    3. Manually move sickle cell images to data/train/sickle/
    4. Run this script to create validation split
    """
    source_path = Path(source_dir)
    sickle_path = Path(sickle_dir)

    if not source_path.exists():
        print(f"Source directory {source_dir} doesn't exist. Run download_kaggle_data.py first.")
        return

    # Create validation directories
    val_normal = Path("data/val/normal")
    val_sickle = Path("data/val/sickle")
    val_normal.mkdir(parents=True, exist_ok=True)
    val_sickle.mkdir(parents=True, exist_ok=True)

    # Get all images
    normal_images = list(source_path.glob("*.jpg")) + list(source_path.glob("*.png"))
    sickle_images = list(sickle_path.glob("*.jpg")) + list(sickle_path.glob("*.png"))

    print(f"Found {len(normal_images)} normal images")
    print(f"Found {len(sickle_images)} sickle images")

    if len(normal_images) == 0 and len(sickle_images) == 0:
        print("No images found. Check your directory structure.")
        return

    # Split 80/20 for validation
    val_normal_count = int(len(normal_images) * 0.2)
    val_sickle_count = int(len(sickle_images) * 0.2)

    # Move to validation
    for i, img in enumerate(normal_images[-val_normal_count:]):
        shutil.move(str(img), str(val_normal / img.name))
        print(f"Moved {img.name} to validation/normal")

    for i, img in enumerate(sickle_images[-val_sickle_count:]):
        shutil.move(str(img), str(val_sickle / img.name))
        print(f"Moved {img.name} to validation/sickle")

    print("✅ Data organization complete!")
    print(f"Train normal: {len(normal_images) - val_normal_count}")
    print(f"Train sickle: {len(sickle_images) - val_sickle_count}")
    print(f"Val normal: {val_normal_count}")
    print(f"Val sickle: {val_sickle_count}")


if __name__ == "__main__":
    organize_sickle_data()