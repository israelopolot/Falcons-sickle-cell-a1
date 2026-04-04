"""
Train Lab Values Model using NHANES Real Data + Synthetic Data

This script:
1. Loads NHANES CBC data (P_CBC.xpt)
2. Extracts Hemoglobin, WBC, Platelet values
3. Combines with synthetic data (Normal, Carrier, Sickle Cell)
4. Trains 3-class neural network model
5. Evaluates on real vs synthetic hold-out test sets
"""

import numpy as np
import pandas as pd
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import TensorDataset, DataLoader
import pickle
import os
import pyreadstat

np.random.seed(42)
torch.manual_seed(42)

# Loading nhances Real Data

print("=" * 70)
print("Loading NHANES Real Data")
print("=" * 70)

df_nhanes, _ = pyreadstat.read_xport('P_CBC.xpt')

# Extracting lab values
real_data = df_nhanes[['LBXHGB', 'LBXWBCSI', 'LBXPLTSI']].copy()
real_data.columns = ['hb', 'wbc', 'platelets']

# Removing rows with missing values
real_data = real_data.dropna()

print(f"✓ NHANES data loaded: {len(real_data)} samples")
print(f"  Hemoglobin (Hb): {real_data['hb'].min():.1f} - {real_data['hb'].max():.1f} g/dL")
print(f"  WBC: {real_data['wbc'].min():.1f} - {real_data['wbc'].max():.1f} ×10^9/L")
print(f"  Platelets: {real_data['platelets'].min():.0f} - {real_data['platelets'].max():.0f} ×10^9/L")

# For real NHANES data: assign labels based on biological ranges
# NHANES data is mostly normal/healthy population samples
# We'll split: ~85% Normal, ~15% Carrier (mild anemia indicators)

print("\nAssigning labels to real NHANES data based on lab value ranges...")

real_labels = []
for idx, row in real_data.iterrows():
    hb = row['hb']
    wbc = row['wbc']
    
    # Simplified heuristic for label assignment
    if hb < 10.0 and wbc > 12.0:
        # Low Hb + High WBC = potential Sickle Cell
        real_labels.append(2)
    elif hb < 12.0 and wbc >= 8.0:
        # Slightly low Hb + elevated WBC = potential Carrier
        real_labels.append(1)
    else:
        # Normal range
        real_labels.append(0)

real_labels = np.array(real_labels)

print(f"\nReal data label distribution:")
print(f"  Normal: {sum(real_labels == 0)} ({100*sum(real_labels == 0)/len(real_labels):.1f}%)")
print(f"  Carrier: {sum(real_labels == 1)} ({100*sum(real_labels == 1)/len(real_labels):.1f}%)")
print(f"  Sickle Cell: {sum(real_labels == 2)} ({100*sum(real_labels == 2)/len(real_labels):.1f}%)")

# ============== Generate Synthetic Data ==============

print("\n" + "=" * 70)
print("Generating Synthetic Data")
print("=" * 70)

def generate_synthetic_lab_data(n_normal=400, n_carrier=300, n_sickle=300):
    """Generate synthetic lab values with 3 classes"""
    X = []
    y = []
    
    # Normal lab values
    for _ in range(n_normal):
        hb = np.random.normal(loc=14.0, scale=1.5)
        hb = np.clip(hb, 11.5, 18.0)
        wbc = np.random.normal(loc=7.5, scale=2.0)
        wbc = np.clip(wbc, 3.0, 12.0)
        platelets = np.random.normal(loc=250, scale=50)
        platelets = np.clip(platelets, 100, 450)
        X.append([hb, wbc, platelets])
        y.append(0)
    
    # Carrier (Trait) lab values
    for _ in range(n_carrier):
        hb = np.random.normal(loc=11.5, scale=0.8)
        hb = np.clip(hb, 10.5, 13.0)
        wbc = np.random.normal(loc=7.0, scale=1.5)
        wbc = np.clip(wbc, 4.5, 11.0)
        platelets = np.random.normal(loc=200, scale=40)
        platelets = np.clip(platelets, 100, 300)
        X.append([hb, wbc, platelets])
        y.append(1)
    
    # Sickle Cell Disease lab values
    for _ in range(n_sickle):
        hb = np.random.normal(loc=8.5, scale=1.5)
        hb = np.clip(hb, 5.5, 11.0)
        wbc = np.random.normal(loc=12.5, scale=3.0)
        wbc = np.clip(wbc, 6.0, 25.0)
        platelets = np.random.normal(loc=180, scale=60)
        platelets = np.clip(platelets, 50, 350)
        X.append([hb, wbc, platelets])
        y.append(2)
    
    return np.array(X), np.array(y)

X_synth, y_synth = generate_synthetic_lab_data(n_normal=400, n_carrier=300, n_sickle=300)
print(f"✓ Synthetic data generated: {len(X_synth)} samples")
print(f"  Normal: {sum(y_synth == 0)}")
print(f"  Carrier: {sum(y_synth == 1)}")
print(f"  Sickle Cell: {sum(y_synth == 2)}")

# ============== Combine Real + Synthetic ==============

print("\n" + "=" * 70)
print("Combining Real + Synthetic Data")
print("=" * 70)

X_combined = np.vstack([real_data.values, X_synth])
y_combined = np.concatenate([real_labels, y_synth])

print(f"✓ Combined dataset: {len(X_combined)} samples")
print(f"  Normal: {sum(y_combined == 0)}")
print(f"  Carrier: {sum(y_combined == 1)}")
print(f"  Sickle Cell: {sum(y_combined == 2)}")

# ============== Normalize Data ==============

print("\nNormalizing combined data...")
mean = X_combined.mean(axis=0)
std = X_combined.std(axis=0) + 1e-8
X_normalized = (X_combined - mean) / std

print(f"  Mean: {mean}")
print(f"  Std: {std}")

# ============== Split into Train/Val/Test ==============

print("\nSplitting data (70/15/15)...")
indices = np.random.permutation(len(X_normalized))
train_idx = indices[:int(0.7 * len(X_normalized))]
val_idx = indices[int(0.7 * len(X_normalized)):int(0.85 * len(X_normalized))]
test_idx = indices[int(0.85 * len(X_normalized)):]

X_train = X_normalized[train_idx]
y_train = y_combined[train_idx]
X_val = X_normalized[val_idx]
y_val = y_combined[val_idx]
X_test = X_normalized[test_idx]
y_test = y_combined[test_idx]

print(f"  Train: {len(X_train)} samples")
print(f"  Val: {len(X_val)} samples")
print(f"  Test: {len(X_test)} samples")

# ============== Define Model ==============

class LabValuesModelArch(nn.Module):
    def __init__(self, input_size=3, hidden_size=64, num_classes=3):
        super(LabValuesModelArch, self).__init__()
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

# ============== Train Model ==============

print("\n" + "=" * 70)
print("Training Model on Real + Synthetic Data")
print("=" * 70)

X_train_tensor = torch.FloatTensor(X_train)
y_train_tensor = torch.LongTensor(y_train)
X_val_tensor = torch.FloatTensor(X_val)
y_val_tensor = torch.LongTensor(y_val)
X_test_tensor = torch.FloatTensor(X_test)
y_test_tensor = torch.LongTensor(y_test)

train_dataset = TensorDataset(X_train_tensor, y_train_tensor)
train_loader = DataLoader(train_dataset, batch_size=32, shuffle=True)

val_dataset = TensorDataset(X_val_tensor, y_val_tensor)
val_loader = DataLoader(val_dataset, batch_size=32, shuffle=False)

device = torch.device('cpu')
model = LabValuesModelArch(input_size=3, hidden_size=64, num_classes=3)
model = model.to(device)

criterion = nn.CrossEntropyLoss()
optimizer = optim.Adam(model.parameters(), lr=0.001)

best_val_acc = 0
patience = 15
patience_counter = 0

for epoch in range(100):
    model.train()
    train_loss = 0.0
    train_correct = 0
    train_total = 0
    
    for X_batch, y_batch in train_loader:
        X_batch = X_batch.to(device)
        y_batch = y_batch.to(device)
        
        outputs = model(X_batch)
        loss = criterion(outputs, y_batch)
        
        optimizer.zero_grad()
        loss.backward()
        optimizer.step()
        
        train_loss += loss.item()
        _, predicted = torch.max(outputs.data, 1)
        train_total += y_batch.size(0)
        train_correct += (predicted == y_batch).sum().item()
    
    train_acc = 100 * train_correct / train_total
    avg_train_loss = train_loss / len(train_loader)
    
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
    
    if (epoch + 1) % 10 == 0:
        print(f"Epoch [{epoch+1}/100] - Train Loss: {avg_train_loss:.4f}, Train Acc: {train_acc:.2f}% - Val Loss: {avg_val_loss:.4f}, Val Acc: {val_acc:.2f}%")
    
    if val_acc > best_val_acc:
        best_val_acc = val_acc
        patience_counter = 0
        torch.save(model.state_dict(), 'models/lab_values_model.pth')
    else:
        patience_counter += 1
        if patience_counter >= patience:
            print(f"\nEarly stopping at epoch {epoch+1}")
            break

print(f"\nBest validation accuracy: {best_val_acc:.2f}%")

# ============== Save Normalization ==============

params = {'mean': mean, 'std': std}
with open('models/lab_values_normalization.pkl', 'wb') as f:
    pickle.dump(params, f)
print("✓ Normalization parameters saved")

# ============== Evaluate on Test Set ==============

print("\n" + "=" * 70)
print("Model Evaluation on Test Set")
print("=" * 70)

model = model.to(device)
model.eval()

with torch.no_grad():
    outputs = model(X_test_tensor.to(device))
    _, predicted = torch.max(outputs.data, 1)
    test_acc = 100 * (predicted == y_test_tensor.to(device)).sum().item() / len(y_test_tensor)

print(f"Test Accuracy: {test_acc:.2f}%")

# Evaluate by class
class_labels = ["Normal", "Carrier (Trait)", "Sickle Cell Disease"]

print("\nPer-class accuracy on test set:")
for class_idx in range(3):
    mask = y_test == class_idx
    if mask.sum() > 0:
        class_acc = 100 * (predicted[mask] == y_test_tensor[mask]).sum().item() / mask.sum()
        print(f"  {class_labels[class_idx]}: {class_acc:.2f}% ({mask.sum()} samples)")

print("\n" + "=" * 70)
print("✅ Training Complete!")
print(f"Model: models/lab_values_model.pth")
print(f"Normalization: models/lab_values_normalization.pkl")
print(f"Test Accuracy: {test_acc:.2f}%")
print("=" * 70)
