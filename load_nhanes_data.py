"""
Script to load NHANES CBC data and extract lab values for model training
"""

import pyreadstat
import pandas as pd
import numpy as np

# Load NHANES CBC data
print("Loading NHANES CBC data from P_CBC.xpt...")
df, meta = pyreadstat.read_xport('P_CBC.xpt')

print(f"\n✓ Data loaded successfully!")
print(f"Shape: {df.shape[0]} rows × {df.shape[1]} columns")
print(f"\nAll columns:")
for i, col in enumerate(df.columns, 1):
    print(f"  {i}. {col}")

print(f"\nFirst 5 rows:")
print(df.head())

print(f"\nData types:")
print(df.dtypes)

print(f"\nMissing values per column:")
print(df.isnull().sum())

# Look for hemoglobin, WBC, platelet columns
print(f"\n\n=== LOOKING FOR LAB VALUES ===")
hb_cols = [col for col in df.columns if 'HGB' in col.upper() or 'HEMOGLOBIN' in col.upper()]
wbc_cols = [col for col in df.columns if 'WBC' in col.upper() or 'WHITE' in col.upper()]
plt_cols = [col for col in df.columns if 'PLT' in col.upper() or 'PLATELET' in col.upper()]

print(f"Hemoglobin columns: {hb_cols}")
print(f"WBC columns: {wbc_cols}")
print(f"Platelet columns: {plt_cols}")
