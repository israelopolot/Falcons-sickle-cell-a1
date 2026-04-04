import cv2
import numpy as np
from PIL import Image
import torch
from torchvision import transforms
import matplotlib.pyplot as plt
from skimage import morphology, measure
import pandas as pd
from inference import load_model, predict_image

def preprocess_smear(image_path, target_size=(224, 224)):
    """Load and preprocess blood smear image"""
    image = cv2.imread(image_path)
    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    return image

def detect_cells(image, min_area=500, max_area=5000):
    """Detect individual blood cells in smear using simple thresholding"""
    # Convert to grayscale
    gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)

    # Apply Gaussian blur to reduce noise
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)

    # Adaptive thresholding to handle varying illumination
    thresh = cv2.adaptiveThreshold(
        blurred, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV, 11, 2
    )

    # Morphological operations to clean up the mask
    kernel = np.ones((3, 3), np.uint8)
    cleaned = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, kernel, iterations=2)
    cleaned = cv2.morphologyEx(cleaned, cv2.MORPH_CLOSE, kernel, iterations=2)

    # Find contours
    contours, _ = cv2.findContours(cleaned, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    # Filter contours by area
    cell_regions = []
    for contour in contours:
        area = cv2.contourArea(contour)
        if min_area < area < max_area:
            # Get bounding box
            x, y, w, h = cv2.boundingRect(contour)
            cell_regions.append((x, y, w, h))

    return cell_regions

def extract_cell_images(image, cell_regions, padding=5):
    """Extract individual cell images from detected regions"""
    cell_images = []
    valid_regions = []

    for x, y, w, h in cell_regions:
        # Add padding
        x1 = max(0, x - padding)
        y1 = max(0, y - padding)
        x2 = min(image.shape[1], x + w + padding)
        y2 = min(image.shape[0], y + h + padding)

        cell_img = image[y1:y2, x1:x2]

        # Skip if too small after padding
        if cell_img.shape[0] < 20 or cell_img.shape[1] < 20:
            continue

        cell_images.append(cell_img)
        valid_regions.append((x1, y1, x2-x1, y2-y1))

    return cell_images, valid_regions

def analyze_smear(image_path, model_path="models/blood_cell_classifier.pth"):
    """Analyze entire blood smear and return cell type counts"""
    # Load model
    model, class_names = load_model(model_path)

    # Preprocess smear
    image = preprocess_smear(image_path)

    # Detect cells
    cell_regions = detect_cells(image)

    if not cell_regions:
        return {"error": "No cells detected in smear"}

    # Extract cell images
    cell_images, valid_regions = extract_cell_images(image, cell_regions)

    # Classify each cell
    predictions = []
    for cell_img in cell_images:
        try:
            # Convert to PIL Image for prediction
            pil_img = Image.fromarray(cell_img)
            pred = predict_image(pil_img, model, class_names)
            predictions.append(pred)
        except Exception as e:
            print(f"Error classifying cell: {e}")
            continue

    # Count cell types
    cell_counts = {}
    for class_name in class_names:
        cell_counts[class_name] = 0

    for pred in predictions:
        cell_type = pred['label']
        if cell_type in cell_counts:
            cell_counts[cell_type] += 1

    # Calculate percentages
    total_cells = len(predictions)
    cell_percentages = {}
    for cell_type, count in cell_counts.items():
        cell_percentages[cell_type] = (count / total_cells * 100) if total_cells > 0 else 0

    # Sickle cell detection logic (if sickle class exists)
    sickle_indicators = []
    if 'sickle' in cell_counts and cell_counts['sickle'] > 0:
        sickle_percentage = cell_percentages['sickle']
        if sickle_percentage > 5:  # Threshold for sickle cell disease
            sickle_indicators.append(f"High sickle cell percentage: {sickle_percentage:.1f}%")
        else:
            sickle_indicators.append(f"Possible sickle cell trait: {sickle_percentage:.1f}%")

    return {
        "total_cells_analyzed": total_cells,
        "cell_counts": cell_counts,
        "cell_percentages": cell_percentages,
        "sickle_indicators": sickle_indicators if sickle_indicators else ["No sickle cells detected"],
        "regions_analyzed": len(valid_regions)
    }

def visualize_smear_analysis(image_path, save_path=None):
    """Create visualization of detected cells on smear"""
    image = preprocess_smear(image_path)
    cell_regions = detect_cells(image)

    # Create figure
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))

    # Original image with bounding boxes
    ax1.imshow(image)
    ax1.set_title("Detected Cells")

    for x, y, w, h in cell_regions:
        rect = plt.Rectangle((x, y), w, h, fill=False, color='red', linewidth=2)
        ax1.add_patch(rect)

    # Cell count histogram
    analysis = analyze_smear(image_path)
    cell_types = list(analysis['cell_counts'].keys())
    counts = list(analysis['cell_counts'].values())

    ax2.bar(cell_types, counts)
    ax2.set_title("Cell Type Distribution")
    ax2.set_ylabel("Count")
    plt.xticks(rotation=45)

    plt.tight_layout()

    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        plt.close()
    else:
        plt.show()

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Analyze blood smear images")
    parser.add_argument("image_path", help="Path to blood smear image")
    parser.add_argument("--model_path", default="models/blood_cell_classifier.pth",
                       help="Path to trained model")
    parser.add_argument("--visualize", action="store_true",
                       help="Create visualization of analysis")

    args = parser.parse_args()

    # Run analysis
    result = analyze_smear(args.image_path, args.model_path)

    print("Blood Smear Analysis Results:")
    print(f"Total cells analyzed: {result['total_cells_analyzed']}")
    print("\nCell counts:")
    for cell_type, count in result['cell_counts'].items():
        print(f"  {cell_type}: {count}")

    print("\nCell percentages:")
    for cell_type, percentage in result['cell_percentages'].items():
        print(f"  {cell_type}: {percentage:.1f}%")

    print("\nSickle cell indicators:")
    for indicator in result['sickle_indicators']:
        print(f"  {indicator}")

    if args.visualize:
        visualize_smear_analysis(args.image_path, "smear_analysis.png")
        print("\nVisualization saved as 'smear_analysis.png'")