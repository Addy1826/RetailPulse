# cleaning.py - Cleans raw CSV data using pandas

import numpy as np
import pandas as pd


def strip_and_fix(df):
    """Strip whitespace and replace placeholder values like 'N/A' with NaN."""
    str_cols = df.select_dtypes(include=["object", "str"]).columns
    df[str_cols] = df[str_cols].apply(lambda s: s.str.strip())
    df = df.replace({"": np.nan, "N/A": np.nan, "n/a": np.nan,
                     "NA": np.nan, "null": np.nan, "None": np.nan,
                     "none": np.nan, "  ": np.nan})
    return df


def clean_customers(df):
    df = strip_and_fix(df)
    df = df.drop_duplicates(subset=["email"], keep="first")
    df["first_name"] = df["first_name"].fillna("Unknown")
    df["join_date"] = pd.to_datetime(df["join_date"], errors="coerce")
    df = df.dropna(subset=["join_date"])

    valid_segments = {"Regular", "Premium", "VIP"}
    df["segment"] = df["segment"].where(df["segment"].isin(valid_segments), "Regular")

    df = df.reset_index(drop=True)
    df["customer_id"] = range(1, len(df) + 1)
    return df


def clean_categories(df):
    df = strip_and_fix(df)
    df = df.drop_duplicates(subset=["category_name"], keep="first")
    df = df.dropna(subset=["category_name"])
    return df


def clean_products(df):
    df = strip_and_fix(df)
    df = df.drop_duplicates(subset=["sku"], keep="first")

    # Cap outlier prices at the 98th percentile
    price_cap = df["unit_price"].quantile(0.98)
    df["unit_price"] = df["unit_price"].clip(upper=price_cap)

    # Make sure cost is always less than selling price
    df.loc[df["cost_price"] >= df["unit_price"], "cost_price"] = df["unit_price"] * 0.6
    df["cost_price"] = df["cost_price"].round(2)
    df["is_active"] = df["is_active"].fillna(1).astype(int)
    return df


def clean_stores(df):
    df = strip_and_fix(df)
    df = df.drop_duplicates(subset=["store_id"], keep="first")
    df["open_date"] = pd.to_datetime(df["open_date"], errors="coerce")
    df = df.dropna(subset=["open_date", "city", "state"])
    return df


def clean_orders(df):
    df = strip_and_fix(df)
    df = df.drop_duplicates(subset=["order_id"], keep="first")
    df["order_date"] = pd.to_datetime(df["order_date"], errors="coerce")
    df = df.dropna(subset=["order_date"])

    valid_statuses = {"Completed", "Returned", "Cancelled"}
    df["status"] = df["status"].where(df["status"].isin(valid_statuses), "Completed")
    df["total_amount"] = pd.to_numeric(df["total_amount"], errors="coerce").fillna(0)
    return df


def clean_order_items(df):
    df = strip_and_fix(df)
    df["quantity"] = pd.to_numeric(df["quantity"], errors="coerce")
    df = df.dropna(subset=["quantity"])
    df["quantity"] = df["quantity"].astype(int).clip(lower=1)
    df["unit_price"] = pd.to_numeric(df["unit_price"], errors="coerce").fillna(0)
    df["discount_pct"] = pd.to_numeric(df["discount_pct"], errors="coerce").fillna(0)
    return df


def clean_inventory(df):
    df = strip_and_fix(df)
    df = df.drop_duplicates(subset=["store_id", "product_id"], keep="first")
    df["qty_on_hand"] = pd.to_numeric(df["qty_on_hand"], errors="coerce").fillna(0).astype(int)
    df["reorder_level"] = pd.to_numeric(df["reorder_level"], errors="coerce").fillna(10).astype(int)
    df["last_restock"] = pd.to_datetime(df["last_restock"], errors="coerce")
    return df
