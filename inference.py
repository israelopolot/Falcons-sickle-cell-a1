from pathlib import Path
from typing import List

import torch
from torchvision import transforms
from PIL import Image


def load_model(model_path: str):
    checkpoint = torch.load(model_path, map_location=torch.device("cpu"))
    classes = checkpoint.get("classes", ["normal", "sickle"])

    model = torch.hub.load('pytorch/vision:v0.15.2', 'resnet18', pretrained=False)
    num_features = model.fc.in_features
    model.fc = torch.nn.Linear(num_features, len(classes))
    model.load_state_dict(checkpoint["model_state"])
    model.eval()

    return model, classes


def preprocess(image_input):
    if isinstance(image_input, (str, Path)):
        image = Image.open(image_input).convert("RGB")
    else:
        # file-like object, BytesIO, UploadFile stream, etc.
        image = Image.open(image_input).convert("RGB")

    transform = transforms.Compose([
        transforms.Resize((224, 224)),
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
    ])
    return transform(image).unsqueeze(0)


def predict(model, classes: List[str], image_tensor):
    with torch.no_grad():
        logits = model(image_tensor)
        probs = torch.softmax(logits, dim=1)[0]
        best_idx = torch.argmax(probs).item()
        return {
            "label": classes[best_idx],
            "confidence": float(probs[best_idx]),
            "probabilities": {classes[i]: float(probs[i]) for i in range(len(classes))},
        }


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Run inference on single image.")
    parser.add_argument("--model_path", type=str, default="models/sickle_classifier.pth")
    parser.add_argument("--image_path", type=str, required=True)
    args = parser.parse_args()

    model, classes = load_model(args.model_path)
    tensor = preprocess(args.image_path)
    result = predict(model, classes, tensor)
    print(result)
