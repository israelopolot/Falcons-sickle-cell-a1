import os
import pandas as pd
import shutil
from pathlib import Path
from sklearn.model_selection import train_test_split


def organize_kaggle_blood_cells(source_dir="data/kaggle_blood_cells", output_dir="data"):
    """
    Organize the downloaded Kaggle blood cells dataset for training.
    This dataset contains WBC classifications, not specifically sickle cells.
    """
    source_path = Path(source_dir)
    output_path = Path(output_dir)

    # Find the actual data location (nested structure)
    labels_file = None
    images_dir = None

    for root, dirs, files in os.walk(source_path):
        if 'labels.csv' in files:
            labels_file = Path(root) / 'labels.csv'
        if 'JPEGImages' in dirs:
            images_dir = Path(root) / 'JPEGImages'

    if not labels_file or not images_dir:
        print("❌ Could not find labels.csv or JPEGImages directory")
        return False

    print(f"Found labels: {labels_file}")
    print(f"Found images: {images_dir}")

    # Read labels
    try:
        df = pd.read_csv(labels_file)
        print(f"Loaded {len(df)} labels")
        
        # Clean categories - remove NaN and complex multi-class labels
        df = df.dropna(subset=['Category'])
        df = df[~df['Category'].str.contains(',', na=False)]  # Remove multi-class labels
        df = df[df['Category'].isin(['NEUTROPHIL', 'EOSINOPHIL', 'LYMPHOCYTE', 'MONOCYTE', 'BASOPHIL'])]
        
        print(f"After cleaning: {len(df)} labels")
        print("Categories:", df['Category'].unique())
    except Exception as e:
        print(f"Error reading labels.csv: {e}")
        return False

    # Create directories
    for split in ['train', 'val']:
        for category in df['Category'].unique():
            (output_path / split / category.lower()).mkdir(parents=True, exist_ok=True)

    # Split data
    train_df, val_df = train_test_split(df, test_size=0.2, random_state=42, stratify=df['Category'])

    print(f"Train: {len(train_df)} images, Val: {len(val_df)} images")

    # Copy images to train
    copied_train = 0
    for _, row in train_df.iterrows():
        img_name = f"BloodImage_{row['Image']:05d}.jpg"
        src_path = images_dir / img_name
        dst_path = output_path / 'train' / row['Category'].lower() / img_name

        if src_path.exists():
            shutil.copy2(src_path, dst_path)
            copied_train += 1
        else:
            print(f"Warning: {src_path} not found")

    # Copy images to val
    copied_val = 0
    for _, row in val_df.iterrows():
        img_name = f"BloodImage_{row['Image']:05d}.jpg"
        src_path = images_dir / img_name
        dst_path = output_path / 'val' / row['Category'].lower() / img_name

        if src_path.exists():
            shutil.copy2(src_path, dst_path)
            copied_val += 1
        else:
            print(f"Warning: {src_path} not found")

    print("\n✅ Dataset organized!")
    print(f"  Train images copied: {copied_train}")
    print(f"  Val images copied: {copied_val}")

    # Show distribution
    print("\nTrain distribution:")
    for category in sorted(df['Category'].unique()):
        count = len(list((output_path / 'train' / category.lower()).glob('*.jpg')))
        print(f"  {category.lower()}: {count}")

    print("\nVal distribution:")
    for category in sorted(df['Category'].unique()):
        count = len(list((output_path / 'val' / category.lower()).glob('*.jpg')))
        print(f"  {category.lower()}: {count}")

    return True


if __name__ == "__main__":
    print("Organizing Kaggle blood cells dataset...")
    success = organize_kaggle_blood_cells()

    if success:
        print("\n🎯 Next steps:")
        print("1. Add sickle cell images to data/train/sickle/ and data/val/sickle/")
        print("2. Run: python train.py --data_dir data --epochs 20 --batch_size 16")
        print("3. Test: python -m uvicorn app.main:app --host 0.0.0.0 --port 8000")
    else:
        print("\n❌ Organization failed. Check dataset structure.")