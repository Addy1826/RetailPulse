# cleaning.py - Data cleaning functions for RetailPulse

import pandas as pd


def clean_customers(df):
    """Clean customers data."""
    df = df.copy()
    # Strip whitespace from string columns
    for col in ["Customer_name", "email", "city"]:
        if col in df.columns:
            df[col] = df[col].astype(str).str.strip()

    # Drop duplicate customers
    df = df.drop_duplicates(subset=["Customer_Id"])
    df = df.drop_duplicates(subset=["email"])

    # Ensure valid signup dates
    df["signup_date"] = pd.to_datetime(df["signup_date"], errors="coerce").dt.strftime("%Y-%m-%d")
    return df.dropna(subset=["Customer_Id", "Customer_name"])


def clean_stores(df):
    """Clean stores data."""
    df = df.copy()
    for col in ["store_name", "city"]:
        if col in df.columns:
            df[col] = df[col].astype(str).str.strip()

    df = df.drop_duplicates(subset=["store_id"])
    df["opening_date"] = pd.to_datetime(df["opening_date"], errors="coerce").dt.strftime("%Y-%m-%d")
    return df.dropna(subset=["store_id", "store_name"])


def clean_products(df):
    """Clean products data."""
    df = df.copy()
    for col in ["product_name", "category"]:
        if col in df.columns:
            df[col] = df[col].astype(str).str.strip()

    df = df.drop_duplicates(subset=["product_id"])
    # Ensure positive unit price
    df["Unit_price"] = pd.to_numeric(df["Unit_price"], errors="coerce")
    df = df[df["Unit_price"] > 0]
    df["reorder_level"] = df["reorder_level"].fillna(10).astype(int)
    return df.dropna(subset=["product_id", "product_name"])


def clean_orders(df):
    """Clean orders data."""
    df = df.copy()
    df = df.drop_duplicates(subset=["order_id"])

    valid_statuses = ["Completed", "Cancelled", "Returned"]
    df["order_status"] = df["order_status"].apply(lambda s: s if s in valid_statuses else "Completed")

    df["Order_date"] = pd.to_datetime(df["Order_date"], errors="coerce").dt.strftime("%Y-%m-%d")
    return df.dropna(subset=["order_id", "Customer_id", "store_id"])


def clean_order_items(df):
    """Clean order items data."""
    df = df.copy()
    # Primary key is (order_id, product_id)
    df = df.drop_duplicates(subset=["order_id", "product_id"])

    df["quantity"] = pd.to_numeric(df["quantity"], errors="coerce").fillna(1).astype(int)
    df["selling_price"] = pd.to_numeric(df["selling_price"], errors="coerce")

    # Only keep positive values
    df = df[(df["quantity"] > 0) & (df["selling_price"] > 0)]
    return df.dropna(subset=["order_id", "product_id"])


def clean_inventory(df):
    """Clean inventory data."""
    df = df.copy()
    # Primary key is (store_id, product_id)
    df = df.drop_duplicates(subset=["store_id", "product_id"])

    df["stock_quantity"] = pd.to_numeric(df["stock_quantity"], errors="coerce").fillna(0).astype(int)
    df = df[df["stock_quantity"] >= 0]
    df["last_updated"] = pd.to_datetime(df["last_updated"], errors="coerce").dt.strftime("%Y-%m-%d")
    return df.dropna(subset=["store_id", "product_id"])
