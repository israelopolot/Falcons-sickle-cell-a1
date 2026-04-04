"""
Train Lab Values Model for Sickle Cell Detection
This script trains a neural network to classify lab values as normal or sickle cell related.
"""

import numpy as np
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import TensorDataset, DataLoader
import pickle
import os

# Set random seeds for reproducibility
np.random.seed(42)
torch.manual_seed(42)

class LabValuesModel(nn.Module):
    """Neural network for lab values classification"""
    def __init__(self, input_size=3, hidden_size=64, num_classes=2):
        super(LabValuesModel, self).__init__()
        self.fc1 = nn.Linear(input_size, hidden_size)
        self.relu1 = nn.ReLU()
        self.dropout1 = nn.Dropout(0.3)
        
        self.fc2 = nn.Linear(hidden_size, hidden_size // 2)
        self.relu2 = nn.ReLU()
        self.dropout2 = nn.Dropout(0.3)
        
        self.fc3 = nn.Linear(hidden_size // 2, num_classes)
    
    def forward(self, x):
        x = self.fc1(x)
        x = self.relu1(x)
        x = self.dropout1(x)
        
        x = self.fc2(x)
        x = self.relu2(x)
        x = self.dropout2(x)
        
        x = self.fc3(x)
        return x


def generate_synthetic_lab_data(n_normal=400, n_carrier=300, n_sickle=300):
    """
    Generate synthetic lab values based on medical research data.
    
    Normal ranges:
    - Hemoglobin (Hb): 12-17.5 g/dL
    - WBC Count: 4.5-11 ×10^9/L
    - Platelets: 150-400 ×10^9/L
    
    Carrier (Sickle Cell Trait) characteristics:
    - Slightly lower Hemoglobin (11-12.5 g/dL)
    - Mildly elevated WBC (6-10 ×10^9/L)
    - Normal to slightly low Platelets (130-250 ×10^9/L)
    
    Sickle Cell Disease characteristics:
    - Lower Hemoglobin (6-10 g/dL)
    - Higher WBC (8-20 ×10^9/L)
    - Lower Platelets (100-200 ×10^9/L)
    """
    X = []
    y = []
    
    # Normal lab values
    print(f"Generating {n_normal} normal lab value samples...")
    for _ in range(n_normal):
        hb = np.random.normal(loc=14.0, scale=1.5)  # Normal: 12-17.5
        hb = np.clip(hb, 11.5, 18.0)
        
        wbc = np.random.normal(loc=7.5, scale=2.0)  # Normal: 4.5-11
        wbc = np.clip(wbc, 3.0, 12.0)
        
        platelets = np.random.normal(loc=250, scale=50)  # Normal: 150-400
        platelets = np.clip(platelets, 100, 450)
        
        X.append([hb, wbc, platelets])
        y.append(0)  # Label 0: Normal
    
    # Carrier (Sickle Cell Trait) lab values
    print(f"Generating {n_carrier} sickle cell carrier lab value samples...")
    for _ in range(n_carrier):
        # Mild anemia in carriers
        hb = np.random.normal(loc=11.5, scale=0.8)  # Mild: 11-12.5
        hb = np.clip(hb, 10.5, 13.0)
        
        # Mildly elevated WBC
        wbc = np.random.normal(loc=7.0, scale=1.5)  # Mildly elevated: 6-10
        wbc = np.clip(wbc, 4.5, 11.0)
        
        # Normal to slightly low platelets
        platelets = np.random.normal(loc=200, scale=40)  # 130-250
        platelets = np.clip(platelets, 100, 300)
        
        X.append([hb, wbc, platelets])
        y.append(1)  # Label 1: Carrier
    
    # Sickle Cell Disease lab values
    print(f"Generating {n_sickle} sickle cell disease lab value samples...")
    for _ in range(n_sickle):
        # Severe anemia in sickle cell disease
        hb = np.random.normal(loc=8.5, scale=1.5)  # Lower: 6-10
        hb = np.clip(hb, 5.5, 11.0)
        
        # Elevated WBC due to chronic hemolysis and inflammation
        wbc = np.random.normal(loc=12.5, scale=3.0)  # Higher: 8-20
        wbc = np.clip(wbc, 6.0, 25.0)
        
        # Lower platelets due to hemolysis
        platelets = np.random.normal(loc=180, scale=60)  # Lower: 100-250
        platelets = np.clip(platelets, 50, 350)
        
        X.append([hb, wbc, platelets])
        y.append(2)  # Label 2: Sickle Cell Disease
    
    return np.array(X), np.array(y)


def normalize_lab_values(X, epsilon=1e-8):
    """Normalize lab values using mean and std"""
    mean = X.mean(axis=0)
    std = X.std(axis=0) + epsilon
    X_normalized = (X - mean) / std
    
    return X_normalized, mean, std


def train_model(X_train, y_train, X_val, y_val, epochs=100, batch_size=32, learning_rate=0.001):
    """Train the lab values model"""
    
    # Convert to tensors
    X_train_tensor = torch.FloatTensor(X_train)
    y_train_tensor = torch.LongTensor(y_train)
    X_val_tensor = torch.FloatTensor(X_val)
    y_val_tensor = torch.LongTensor(y_val)
    
    # Create datasets and dataloaders
    train_dataset = TensorDataset(X_train_tensor, y_train_tensor)
    train_loader = DataLoader(train_dataset, batch_size=batch_size, shuffle=True)
    
    val_dataset = TensorDataset(X_val_tensor, y_val_tensor)
    val_loader = DataLoader(val_dataset, batch_size=batch_size, shuffle=False)
    
    # Initialize model
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    print(f"Using device: {device}")
    
    model = LabValuesModel(input_size=3, hidden_size=64, num_classes=3)
    model = model.to(device)
    
    # Loss and optimizer
    criterion = nn.CrossEntropyLoss()
    optimizer = optim.Adam(model.parameters(), lr=learning_rate)
    
    # Training loop
    print("\nStarting training...")
    best_val_acc = 0
    patience = 15
    patience_counter = 0
    
    for epoch in range(epochs):
        # Training phase
        model.train()
        train_loss = 0.0
        train_correct = 0
        train_total = 0
        
        for X_batch, y_batch in train_loader:
            X_batch = X_batch.to(device)
            y_batch = y_batch.to(device)
            
            # Forward pass
            outputs = model(X_batch)
            loss = criterion(outputs, y_batch)
            
            # Backward pass
            optimizer.zero_grad()
            loss.backward()
            optimizer.step()
            
            # Stats
            train_loss += loss.item()
            _, predicted = torch.max(outputs.data, 1)
            train_total += y_batch.size(0)
            train_correct += (predicted == y_batch).sum().item()
        
        train_acc = 100 * train_correct / train_total
        avg_train_loss = train_loss / len(train_loader)
        
        # Validation phase
        model.eval()
        val_loss = 0.0
        val_correct = 0
        val_total = 0
        
        with torch.no_grad():
            for X_batch, y_batch in val_loader:
                X_batch = X_batch.to(device)
                y_batch = y_batch.to(device)
                
                outputs = model(X_batch)
                loss = criterion(outputs, y_batch)
                
                val_loss += loss.item()
                _, predicted = torch.max(outputs.data, 1)
                val_total += y_batch.size(0)
                val_correct += (predicted == y_batch).sum().item()
        
        val_acc = 100 * val_correct / val_total
        avg_val_loss = val_loss / len(val_loader)
        
        # Print progress
        if (epoch + 1) % 10 == 0:
            print(f"Epoch [{epoch+1}/{epochs}] - Train Loss: {avg_train_loss:.4f}, "
                  f"Train Acc: {train_acc:.2f}% - Val Loss: {avg_val_loss:.4f}, Val Acc: {val_acc:.2f}%")
        
        # Early stopping
        if val_acc > best_val_acc:
            best_val_acc = val_acc
            patience_counter = 0
            # Save best model
            torch.save(model.state_dict(), 'models/lab_values_model.pth')
        else:
            patience_counter += 1
            if patience_counter >= patience:
                print(f"\nEarly stopping at epoch {epoch+1}")
                break
    
    print(f"\nTraining complete! Best validation accuracy: {best_val_acc:.2f}%")
    return model


def save_normalization_params(mean, std):
    """Save normalization parameters for inference"""
    params = {
        'mean': mean,
        'std': std
    }
    with open('models/lab_values_normalization.pkl', 'wb') as f:
        pickle.dump(params, f)
    print("Saved normalization parameters to models/lab_values_normalization.pkl")


def main():
    """Main training pipeline"""
    
    print("=" * 60)
    print("Lab Values Model Training Pipeline")
    print("=" * 60)
    
    # Create models directory if it doesn't exist
    os.makedirs('models', exist_ok=True)
    
    # Generate synthetic data
    print("\n[1/4] Generating synthetic lab values data...")
    X, y = generate_synthetic_lab_data(n_normal=400, n_carrier=300, n_sickle=300)
    print(f"Generated {len(X)} samples")
    print(f"  - Normal: {sum(y == 0)}")
    print(f"  - Carrier (Trait): {sum(y == 1)}")
    print(f"  - Sickle Cell Disease: {sum(y == 2)}")
    
    # Normalize data
    print("\n[2/4] Normalizing lab values...")
    X_normalized, mean, std = normalize_lab_values(X)
    print(f"Normalization parameters:")
    print(f"  - Mean: {mean}")
    print(f"  - Std: {std}")
    
    # Split into train/val/test
    print("\n[3/4] Splitting data into train/val/test sets...")
    indices = np.random.permutation(len(X_normalized))
    train_idx = indices[:int(0.7 * len(X_normalized))]
    val_idx = indices[int(0.7 * len(X_normalized)):int(0.85 * len(X_normalized))]
    test_idx = indices[int(0.85 * len(X_normalized)):]
    
    X_train = X_normalized[train_idx]
    y_train = y[train_idx]
    X_val = X_normalized[val_idx]
    y_val = y[val_idx]
    X_test = X_normalized[test_idx]
    y_test = y[test_idx]
    
    print(f"  - Train: {len(X_train)} samples")
    print(f"  - Val: {len(X_val)} samples")
    print(f"  - Test: {len(X_test)} samples")
    
    # Train model
    print("\n[4/4] Training neural network model...")
    model = train_model(X_train, y_train, X_val, y_val, epochs=100, batch_size=32, learning_rate=0.001)
    
    # Save normalization params
    save_normalization_params(mean, std)
    
    # Test the model
    print("\n" + "=" * 60)
    print("Model Evaluation")
    print("=" * 60)
    
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    model = model.to(device)
    model.eval()
    
    X_test_tensor = torch.FloatTensor(X_test).to(device)
    y_test_tensor = torch.LongTensor(y_test).to(device)
    
    with torch.no_grad():
        outputs = model(X_test_tensor)
        _, predicted = torch.max(outputs.data, 1)
        test_acc = 100 * (predicted == y_test_tensor).sum().item() / len(y_test_tensor)
    
    print(f"Test Accuracy: {test_acc:.2f}%")
    
    # Print example predictions
    print("\nExample predictions:")
    print("(Hb, WBC, Platelets) -> Prediction -> Confidence")
    print("-" * 60)
    
    class_labels = ["Normal", "Carrier (Trait)", "Sickle Cell Disease"]
    
    with torch.no_grad():
        for i in range(min(5, len(X_test))):
            sample = X_test_tensor[i:i+1]
            output = model(sample)
            probs = torch.softmax(output, dim=1)[0]
            pred = torch.argmax(output, dim=1)[0].item()
            confidence = probs[pred].item() * 100
            
            # Denormalize for display
            original_values = X_test[i] * std + mean
            hb, wbc, platelets = original_values
            label = class_labels[pred]
            actual = class_labels[y_test[i]]
            
            print(f"({hb:.1f}, {wbc:.1f}, {platelets:.0f}) -> {label} ({confidence:.1f}%) [Actual: {actual}]")
    
    print("\n" + "=" * 60)
    print("✅ Training complete!")
    print("Model saved to: models/lab_values_model.pth")
    print("Normalization params saved to: models/lab_values_normalization.pkl")
    print("=" * 60)


if __name__ == "__main__":
    main()
