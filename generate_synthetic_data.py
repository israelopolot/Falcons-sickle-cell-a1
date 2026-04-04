import argparse
import os
from pathlib import Path

import cv2
import numpy as np


def generate_normal_rbc(size=128, num_cells=3):
    """Generate synthetic normal RBC image (circular cells)."""
    img = np.ones((size, size, 3), dtype=np.uint8) * 255  # white background
    
    for _ in range(num_cells):
        center_x = np.random.randint(30, size - 30)
        center_y = np.random.randint(30, size - 30)
        radius = np.random.randint(15, 25)
        color = (np.random.randint(50, 150), np.random.randint(100, 200), np.random.randint(50, 150))
        
        cv2.circle(img, (center_x, center_y), radius, color, -1)
        cv2.circle(img, (center_x, center_y), radius, (0, 0, 0), 1)
    
    # Add noise
    noise = np.random.normal(0, 5, img.shape)
    img = np.clip(img.astype(float) + noise, 0, 255).astype(np.uint8)
    
    return img


def generate_sickled_rbc(size=128, num_cells=3):
    """Generate synthetic sickled RBC image (crescent/elongated cells)."""
    img = np.ones((size, size, 3), dtype=np.uint8) * 255  # white background
    
    for _ in range(num_cells):
        center_x = np.random.randint(30, size - 30)
        center_y = np.random.randint(30, size - 30)
        angle = np.random.randint(0, 180)
        color = (np.random.randint(50, 100), np.random.randint(50, 100), np.random.randint(100, 180))
        
        # Draw elongated ellipse (crescent-like shape)
        axes = (np.random.randint(20, 28), np.random.randint(10, 16))
        cv2.ellipse(img, (center_x, center_y), axes, angle, 0, 360, color, -1)
        cv2.ellipse(img, (center_x, center_y), axes, angle, 0, 360, (0, 0, 0), 1)
    
    # noise
    noise = np.random.normal(0, 5, img.shape)
    img = np.clip(img.astype(float) + noise, 0, 255).astype(np.uint8)
    
    return img


def generate_dataset(output_dir, n_images=200, img_size=128):
    """Generate synthetic dataset."""
    output_dir = Path(output_dir)
    
    #  directory structure
    dirs = [
        output_dir / "train" / "normal",
        output_dir / "train" / "sickle",
        output_dir / "val" / "normal",
        output_dir / "val" / "sickle",
    ]
    
    for d in dirs:
        d.mkdir(parents=True, exist_ok=True)
    
    # Split: 80% train, 20% val
    train_count = int(n_images * 0.8)
    val_count = n_images - train_count
    
    print(f"Generating {n_images} images (train={train_count}, val={val_count})...")
    
    # Generate training images
    for i in range(train_count):
        if i % 2 == 0:
            img = generate_normal_rbc(size=img_size)
            path = dirs[0] / f"normal_{i:04d}.jpg"
        else:
            img = generate_sickled_rbc(size=img_size)
            path = dirs[1] / f"sickle_{i:04d}.jpg"
        
        cv2.imwrite(str(path), img)
        if (i + 1) % 50 == 0:
            print(f"  Generated {i + 1} training images...")
    
    # Generate validation images
    for i in range(val_count):
        if i % 2 == 0:
            img = generate_normal_rbc(size=img_size)
            path = dirs[2] / f"normal_{train_count + i:04d}.jpg"
        else:
            img = generate_sickled_rbc(size=img_size)
            path = dirs[3] / f"sickle_{train_count + i:04d}.jpg"
        
        cv2.imwrite(str(path), img)
        if (i + 1) % 10 == 0:
            print(f"  Generated {train_count + i + 1} total images...")
    
    print(f"✓ Dataset created at {output_dir}")
    print(f"  - {dirs[0]}: {len(list(dirs[0].glob('*.jpg')))} images")
    print(f"  - {dirs[1]}: {len(list(dirs[1].glob('*.jpg')))} images")
    print(f"  - {dirs[2]}: {len(list(dirs[2].glob('*.jpg')))} images")
    print(f"  - {dirs[3]}: {len(list(dirs[3].glob('*.jpg')))} images")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate synthetic sickle cell microscope images")
    parser.add_argument("--output_dir", type=str, default="data", help="Output directory")
    parser.add_argument("--n_images", type=int, default=200, help="Total number of images to generate")
    parser.add_argument("--img_size", type=int, default=128, help="Image size (square)")
    
    args = parser.parse_args()
    generate_dataset(args.output_dir, args.n_images, args.img_size)
