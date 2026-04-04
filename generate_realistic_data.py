import os
import json
from pathlib import Path
from sklearn.model_selection import train_test_split
from PIL import Image
import numpy as np
import shutil


def generate_realistic_synthetic_data(output_dir="data", n_images=500):
    """
    Generate MORE REALISTIC synthetic blood cell images using better morphology.
    This bridges gap until real data is available.
    """
    try:
        import cv2
    except ImportError:
        print("OpenCV not found, installing...")
        os.system(".venv\\Scripts\\pip install opencv-python")
        import cv2
    
    output_path = Path(output_dir)
    
    # Create directories
    for split in ['train', 'val']:
        for cell_type in ['normal', 'sickle']:
            (output_path / split / cell_type).mkdir(parents=True, exist_ok=True)
    
    def create_normal_cells(size=224):
        """Create realistic normal (biconcave disc) RBCs."""
        img = np.ones((size, size, 3), dtype=np.uint8) * 240  # light background
        
        num_cells = np.random.randint(2, 5)
        for _ in range(num_cells):
            cx = np.random.randint(40, size - 40)
            cy = np.random.randint(40, size - 40)
            
            # Biconcave disc shape - approximate with two overlapping ellipses
            major_axis = np.random.randint(35, 50)
            minor_axis = np.random.randint(25, 35)
            
            # Main cell body
            color = (np.random.randint(80, 140), np.random.randint(100, 180), np.random.randint(60, 120))
            cv2.ellipse(img, (cx, cy), (major_axis, minor_axis), 0, 0, 360, color, -1)
            
            # Add biconcave depression in center (darker)
            inner_color = tuple(int(c * 0.7) for c in color)
            cv2.ellipse(img, (cx, cy), (int(major_axis * 0.4), int(minor_axis * 0.6)), 
                       0, 0, 360, inner_color, -1)
            
            # Edge highlight
            cv2.ellipse(img, (cx, cy), (major_axis, minor_axis), 0, 0, 360, (50, 50, 50), 2)
        
        # Add noise
        noise = np.random.normal(0, 8, img.shape)
        img = np.clip(img.astype(float) + noise, 0, 255).astype(np.uint8)
        
        return img
    
    def create_sickle_cells(size=224):
        """Create realistic sickled (crescent/elongated) RBCs."""
        img = np.ones((size, size, 3), dtype=np.uint8) * 240
        
        num_cells = np.random.randint(2, 5)
        for _ in range(num_cells):
            cx = np.random.randint(40, size - 40)
            cy = np.random.randint(40, size - 40)
            angle = np.random.randint(0, 180)
            
            # Elongated, crescent-like shape
            major_axis = np.random.randint(40, 65)  # longer
            minor_axis = np.random.randint(15, 25)  # narrower - more elongated
            
            color = (np.random.randint(70, 120), np.random.randint(80, 150), np.random.randint(100, 170))
            
            # Draw elongated ellipse (crescent)
            cv2.ellipse(img, (cx, cy), (major_axis, minor_axis), angle, 0, 360, color, -1)
            
            # Add curvature by overlaying a lighter crescent
            crescent_color = (np.random.randint(100, 150), np.random.randint(120, 180), np.random.randint(130, 200))
            cv2.ellipse(img, (cx - int(major_axis * 0.2), cy), 
                       (int(major_axis * 0.5), int(minor_axis * 0.8)), 
                       angle, 0, 360, crescent_color, -1)
            
            # Edge
            cv2.ellipse(img, (cx, cy), (major_axis, minor_axis), angle, 0, 360, (30, 30, 30), 2)
        
        # Add noise
        noise = np.random.normal(0, 8, img.shape)
        img = np.clip(img.astype(float) + noise, 0, 255).astype(np.uint8)
        
        return img
    
    print(f"Generating {n_images} realistic synthetic blood cell images...")
    
    train_count = int(n_images * 0.8)
    val_count = n_images - train_count
    
    # Generate training images
    for i in range(train_count):
        if i % 2 == 0:
            img = create_normal_cells()
            path = output_path / 'train' / 'normal' / f'normal_{i:05d}.jpg'
        else:
            img = create_sickle_cells()
            path = output_path / 'train' / 'sickle' / f'sickle_{i:05d}.jpg'
        
        Image.fromarray(img).save(path, quality=95)
        
        if (i + 1) % 100 == 0:
            print(f"  Generated {i + 1} training images...")
    
    # Generate validation images
    for i in range(val_count):
        if i % 2 == 0:
            img = create_normal_cells()
            path = output_path / 'val' / 'normal' / f'normal_{train_count + i:05d}.jpg'
        else:
            img = create_sickle_cells()
            path = output_path / 'val' / 'sickle' / f'sickle_{train_count + i:05d}.jpg'
        
        Image.fromarray(img).save(path, quality=95)
        
        if (i + 1) % 50 == 0:
            print(f"  Generated {train_count + i + 1} total images...")
    
    print(f"\n✅ Realistic dataset created!")
    print(f"  Train normal: {len(list((output_path / 'train' / 'normal').glob('*.jpg')))}")
    print(f"  Train sickle: {len(list((output_path / 'train' / 'sickle').glob('*.jpg')))}")
    print(f"  Val normal: {len(list((output_path / 'val' / 'normal').glob('*.jpg')))}")
    print(f"  Val sickle: {len(list((output_path / 'val' / 'sickle').glob('*.jpg')))}")
    
    return True


def main():
    print("="*60)
    print("BLOOD CELL DATA STRATEGY")
    print("="*60)
    print("\nOption 1: Use REALISTIC synthetic data (fastest, works immediately)")
    print("Option 2: Bring your own real images manually")
    print("\nGenerating high-quality synthetic data with realistic morphology...")
    print("(Once you have real data, simply replace images in data/train and data/val)")
    print("="*60 + "\n")
    
    success = generate_realistic_synthetic_data("data", n_images=500)
    
    if success:
        print("\n✅ Ready to train!")
        print("Next command:")
        print("  python train.py --data_dir data --epochs 20 --batch_size 32 --model_path models/sickle_classifier.pth")


if __name__ == "__main__":
    main()
