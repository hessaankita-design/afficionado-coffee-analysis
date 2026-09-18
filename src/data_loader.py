"""
Data Ingestion & Validation Module for Afficionado Coffee Roasters
Handles loading from Excel/CSV, validation, and revenue computation.
"""
import pandas as pd
import numpy as np
import pathlib

def load_data(file_path: str) -> pd.DataFrame:
    """Load transaction data from Excel or CSV."""
    path = pathlib.Path(file_path)
    if not path.exists():
        raise FileNotFoundError(f"Data file not found: {file_path}")
    
    if path.suffix in [".xlsx", ".xls"]:
        df = pd.read_excel(file_path)
    else:
        df = pd.read_csv(file_path)
    
    # Standardize column names
    df.columns = df.columns.str.strip()
    return df

def validate_data(df: pd.DataFrame) -> pd.DataFrame:
    """Validate product identifiers, prices, and quantities."""
    # Check required columns
    required = ["transaction_qty", "unit_price", "product_id"]
    for col in required:
        if col not in df.columns:
            raise ValueError(f"Missing required column: {col}")
    
    # Remove invalid quantities
    initial = len(df)
    df = df[df["transaction_qty"] > 0]
    df = df[df["transaction_qty"] < 20]  # realistic upper bound
    
    # Validate prices
    df = df[df["unit_price"] > 0]
    df = df[df["unit_price"] < 100]  # filter outliers, keep beans/merch separate logic if needed
    
    # Drop missing product identifiers
    df = df.dropna(subset=["product_id", "product_category"])
    
    print(f"Validation: {initial} -> {len(df)} rows ({initial-len(df)} removed)")
    return df

def compute_revenue(df: pd.DataFrame) -> pd.DataFrame:
    """Compute revenue at transaction level."""
    df = df.copy()
    if "Revenue" not in df.columns:
        df["Revenue"] = df["transaction_qty"] * df["unit_price"]
    return df

def enrich_data(df: pd.DataFrame) -> pd.DataFrame:
    """Add derived fields for analysis."""
    df = df.copy()
    # Size extraction from product_detail
    def extract_size(detail):
        if pd.isna(detail):
            return "Unknown"
        d = str(detail)
        if " Lg" in d: return "Large"
        if " Rg" in d: return "Regular"
        if " Sm" in d: return "Small"
        return "Standard"
    
    if "product_detail" in df.columns:
        df["size"] = df["product_detail"].apply(extract_size)
    
    # Time parsing
    if "transaction_time" in df.columns:
        try:
            df["hour"] = pd.to_datetime(df["transaction_time"], format="%H:%M:%S").dt.hour
        except:
            df["hour"] = 12
    return df

def load_and_prepare(file_path: str) -> pd.DataFrame:
    df = load_data(file_path)
    df = validate_data(df)
    df = compute_revenue(df)
    df = enrich_data(df)
    return df
