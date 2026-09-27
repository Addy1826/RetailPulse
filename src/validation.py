# validation.py - Checks cleaned data before loading into MySQL

import pandas as pd


class ValidationError(Exception):
    pass


def check_no_nulls(df, columns, table_name):
    """Ensure specified columns have no missing values."""
    for col in columns:
        if col in df.columns and df[col].isnull().any():
            raise ValidationError(f"Table '{table_name}' has null values in column '{col}'")


def check_positive_values(df, columns, table_name):
    """Ensure numeric columns are greater than zero."""
    for col in columns:
        if col in df.columns and (df[col] <= 0).any():
            raise ValidationError(f"Table '{table_name}' has non-positive values in column '{col}'")


def validate_all_data(cust_df, store_df, prod_df, ord_df, item_df, inv_df):
    """Run full validation checks across all 6 tables."""
    # 1. Primary key checks
    check_no_nulls(cust_df, ["Customer_Id", "Customer_name"], "Customers")
    check_no_nulls(store_df, ["store_id", "store_name"], "stores")
    check_no_nulls(prod_df, ["product_id", "product_name", "Unit_price"], "products")
    check_no_nulls(ord_df, ["order_id", "Customer_id", "store_id"], "orders")
    check_no_nulls(item_df, ["order_id", "product_id", "quantity", "selling_price"], "order_items")
    check_no_nulls(inv_df, ["store_id", "product_id", "stock_quantity"], "inventory")

    # 2. Value checks
    check_positive_values(prod_df, ["Unit_price"], "products")
    check_positive_values(item_df, ["quantity", "selling_price"], "order_items")

    # 3. Foreign key consistency
    cust_ids = set(cust_df["Customer_Id"])
    store_ids = set(store_df["store_id"])
    prod_ids = set(prod_df["product_id"])
    ord_ids = set(ord_df["order_id"])

    if not set(ord_df["Customer_id"]).issubset(cust_ids):
        raise ValidationError("Orders contains Customer_ids not found in Customers table")

    if not set(ord_df["store_id"]).issubset(store_ids):
        raise ValidationError("Orders contains store_ids not found in stores table")

    if not set(item_df["order_id"]).issubset(ord_ids):
        raise ValidationError("Order_items contains order_ids not found in orders table")

    if not set(item_df["product_id"]).issubset(prod_ids):
        raise ValidationError("Order_items contains product_ids not found in products table")

    if not set(inv_df["store_id"]).issubset(store_ids):
        raise ValidationError("Inventory contains store_ids not found in stores table")

    if not set(inv_df["product_id"]).issubset(prod_ids):
        raise ValidationError("Inventory contains product_ids not found in products table")

    return True
