import os
import shutil
from pathlib import Path
from sklearn.model_selection import train_test_split
import kaggle


def download_kaggle_dataset(dataset_slug, output_dir):
    """Download dataset from Kaggle."""
    print(f"Downloading {dataset_slug} from Kaggle...")
    kaggle.api.dataset_download_files(dataset_slug, path=output_dir, unzip=True)
    print(f"Downloaded to {output_dir}")


def organize_blood_cells(source_dir, output_dir, test_size=0.2):
    """Organize blood cell images into train/val splits."""
    source_path = Path(source_dir)
    output_path = Path(output_dir)

    # Create directories
    for split in ['train', 'val']:
        for cell_type in ['normal', 'sickle']:
            (output_path / split / cell_type).mkdir(parents=True, exist_ok=True)

    # Find all image files (assuming RBC images are in a subdirectory)
    # Adjust this based on actual Kaggle dataset structure
    image_extensions = {'.jpg', '.jpeg', '.png', '.bmp'}

    # For blood cell datasets, look for RBC/normal cell images
    # This is a generic organizer - you may need to adjust paths
    all_images = []
    for ext in image_extensions:
        all_images.extend(list(source_path.rglob(f'*{ext}')))

    print(f"Found {len(all_images)} images")

    # For now, we'll assume you manually label some as 'normal' vs 'sickle'
    # In a real scenario, you'd have pre-labeled data
    # For demo, let's split randomly (you'll need to organize manually)

    if len(all_images) > 0:
        # Split into train/val
        train_images, val_images = train_test_split(
            all_images, test_size=test_size, random_state=42
        )

        # Copy to train directory (you'll need to organize into normal/sickle subdirs)
        for img in train_images:
            shutil.copy2(img, output_path / 'train' / 'normal' / img.name)

        for img in val_images:
            shutil.copy2(img, output_path / 'val' / 'normal' / img.name)

        print(f"Organized {len(train_images)} train, {len(val_images)} val images")
        print("⚠️  IMPORTANT: Manually move sickle cell images to 'sickle' subdirectories!")
    else:
        print("No images found. Check dataset structure and update paths.")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Download and organize Kaggle blood cell dataset")
    parser.add_argument("--dataset", type=str, default="hrishikeshp27/blood-cells",
                       help="Kaggle dataset slug (owner/dataset-name)")
    parser.add_argument("--output_dir", type=str, default="data",
                       help="Output directory for organized data")

    args = parser.parse_args()

    # Download
    download_kaggle_dataset(args.dataset, "temp_kaggle_data")

    # Organize
    organize_blood_cells("temp_kaggle_data", args.output_dir)

    # Cleanup
    shutil.rmtree("temp_kaggle_data", ignore_errors=True)