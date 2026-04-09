"""
Script to load NHANES CBC data and extract lab values for model training
"""

import pyreadstat
import pandas as pd
import numpy as np

def load_nhanes_lab_data():
    """
    Load NHANES CBC data and extract relevant lab values.
    
    Returns:
        pd.DataFrame: Clean lab values with columns [hemoglobin, wbc, rbc, rdw, platelets]
    """
    # Load NHANES CBC data
    print("Loading NHANES CBC data from P_CBC.xpt...")
    df, meta = pyreadstat.read_xport('P_CBC.xpt')
    
    print(f"✓ Data loaded successfully! Shape: {df.shape[0]} rows × {df.shape[1]} columns")
    
    # Extract relevant lab value columns
    lab_columns = {
        'hemoglobin': 'LBXHGB',    # Hemoglobin (g/dL)
        'wbc': 'LBXWBCSI',         # WBC count (10^9/L)
        'rbc': 'LBXRBCSI',         # RBC count (10^12/L)
        'rdw': 'LBXRDW',           # RDW (%)
        'platelets': 'LBXPLTSI'    # Platelets (10^9/L)
    }
    
    # Create new dataframe with selected columns
    lab_df = df[list(lab_columns.values())].copy()
    lab_df.columns = list(lab_columns.keys())
    
    # Remove rows with any missing values
    initial_count = len(lab_df)
    lab_df = lab_df.dropna()
    final_count = len(lab_df)
    
    print(f"Extracted {len(lab_columns)} lab value columns")
    print(f"Removed {initial_count - final_count} rows with missing values")
    print(f"Final dataset: {final_count} complete lab value samples")
    
    # Basic statistics
    print(f"\nLab value statistics:")
    print(lab_df.describe())
    
    # Check for reasonable ranges (basic data quality check)
    print(f"\nData quality checks:")
    print(f"Hemoglobin range: {lab_df['hemoglobin'].min():.1f} - {lab_df['hemoglobin'].max():.1f} g/dL")
    print(f"WBC range: {lab_df['wbc'].min():.1f} - {lab_df['wbc'].max():.1f} ×10^9/L")
    print(f"RBC range: {lab_df['rbc'].min():.2f} - {lab_df['rbc'].max():.2f} ×10^12/L")
    print(f"RDW range: {lab_df['rdw'].min():.1f} - {lab_df['rdw'].max():.1f} %")
    print(f"Platelets range: {lab_df['platelets'].min():.0f} - {lab_df['platelets'].max():.0f} ×10^9/L")
    
    return lab_df

if __name__ == "__main__":
    # Load and display the data
    nhanes_data = load_nhanes_lab_data()
    print(f"\nFirst 5 rows of processed NHANES data:")
    print(nhanes_data.head())
