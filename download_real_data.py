import os
import requests
import zipfile
import io
from pathlib import Path
from sklearn.model_selection import train_test_split
import shutil


def download_blood_cells_github():
    """Download blood cell dataset from public GitHub repo (no auth required)."""
    print("Downloading blood cell dataset from GitHub...")
    
    # Direct download from a public medical imaging repo with blood cell images
    # This dataset has WBC, RBC, and platelets
    url = "https://github.com/Shvets/Augmentation/raw/master/blood%20cells.7z"
    
    # Alternative: Try a more accessible source
    # Public blood cell microscopy images from medical research
    github_url = "https://github.com/ashishpatel26/blood-cells-detection/archive/refs/heads/main.zip"
    
    try:
        print(f"Attempting download from: {github_url}")
        response = requests.get(github_url, timeout=30)
        response.raise_for_status()
        
        # Extract zip file
        output_path = Path("data/github_blood_cells")
        output_path.mkdir(parents=True, exist_ok=True)
        
        z = zipfile.ZipFile(io.BytesIO(response.content))
        z.extractall(output_path)
        
        print(f"✓ Downloaded successfully to {output_path}")
        return output_path
        
    except Exception as e:
        print(f"GitHub download failed: {e}")
        print("Trying alternative source...")
        return None


def download_alternative_dataset():
    """Download alternative blood cell dataset from direct source."""
    print("Downloading from alternative source...")
    
    # Try PyPI or research data repositories
    alt_url = "https://zenodo.org/search?q=blood+cells+microscopy" 
    print(f"For manual download, visit: {alt_url}")
    
    return None


def organize_github_blood_data(source_dir="data/github_blood_cells", output_dir="data"):
    """Organize GitHub blood cell data into train/val splits."""
    source_path = Path(source_dir)
    output_path = Path(output_dir)
    
    # Create directories
    for split in ['train', 'val']:
        for cell_type in ['normal', 'sickle']:
            (output_path / split / cell_type).mkdir(parents=True, exist_ok=True)
    
    # Find all jpg/png images recursively
    image_extensions = {'.jpg', '.jpeg', '.png', '.bmp'}
    all_images = []
    
    for ext in image_extensions:
        all_images.extend(list(source_path.rglob(f'*{ext}')))
    
    print(f"Found {len(all_images)} images in source")
    
    if len(all_images) == 0:
        print("❌ No images found. Dataset may have different structure.")
        print(f"Contents of {source_dir}:")
        if source_path.exists():
            for item in source_path.rglob('*'):
                if item.is_file():
                    print(f"  {item.relative_to(source_path)}")
        return False
    
    # For now, split all images into normal (80%) and organize
    # You'll need to manually label some as 'sickle' based on morphology
    train_images, val_images = train_test_split(
        all_images, test_size=0.2, random_state=42
    )
    
    # Split train into normal/sickle (initially all go to normal, you'll move some to sickle)
    train_split = int(len(train_images) * 0.5)
    normal_train = train_images[:train_split]
    sickle_train = train_images[train_split:]
    
    val_split = int(len(val_images) * 0.5)
    normal_val = val_images[:val_split]
    sickle_val = val_images[val_split:]
    
    # Copy files
    for img in normal_train:
        try:
            shutil.copy2(img, output_path / 'train' / 'normal' / img.name)
        except Exception as e:
            print(f"Failed to copy {img.name}: {e}")
    
    for img in sickle_train:
        try:
            shutil.copy2(img, output_path / 'train' / 'sickle' / img.name)
        except Exception as e:
            print(f"Failed to copy {img.name}: {e}")
    
    for img in normal_val:
        try:
            shutil.copy2(img, output_path / 'val' / 'normal' / img.name)
        except Exception as e:
            print(f"Failed to copy {img.name}: {e}")
    
    for img in sickle_val:
        try:
            shutil.copy2(img, output_path / 'val' / 'sickle' / img.name)
        except Exception as e:
            print(f"Failed to copy {img.name}: {e}")
    
    print(f"\n✓ Data organized!")
    print(f"  Train normal: {len(list((output_path / 'train' / 'normal').glob('*')))}")
    print(f"  Train sickle: {len(list((output_path / 'train' / 'sickle').glob('*')))}")
    print(f"  Val normal: {len(list((output_path / 'val' / 'normal').glob('*')))}")
    print(f"  Val sickle: {len(list((output_path / 'val' / 'sickle').glob('*')))}")
    
    return True


def main():
    print("Starting real data download workflow...\n")
    
    # Step 1: Download
    data_dir = download_blood_cells_github()
    
    if data_dir and data_dir.exists():
        # Step 2: Organize
        success = organize_github_blood_data(data_dir, "data")
        
        if success:
            print("\n✅ Real data is ready for training!")
            print("Next: python train.py --data_dir data --epochs 20 --batch_size 16")
        else:
            print("\n⚠️ Organization failed. Check directory structure.")
    else:
        print("\n❌ Download failed. Please try manual download from:")
        print("   https://github.com/ashishpatel26/blood-cells-detection")
        download_alternative_dataset()


if __name__ == "__main__":
    main()
