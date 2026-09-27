# clean_data.py - Cleans raw CSVs and saves to data/processed/

import sys
from pathlib import Path
import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from src.cleaning import (
    clean_customers, clean_stores, clean_products,
    clean_orders, clean_order_items, clean_inventory
)

RAW_DIR = PROJECT_ROOT / "data" / "raw"
PROCESSED_DIR = PROJECT_ROOT / "data" / "processed"
PROCESSED_DIR.mkdir(parents=True, exist_ok=True)


def run_cleaning():
    print("Reading and cleaning data...")

    # 1. Customers
    cust_df = clean_customers(pd.read_csv(RAW_DIR / "Customers.csv"))
    cust_df.to_csv(PROCESSED_DIR / "Customers.csv", index=False)
    print(f"  Cleaned Customers: {len(cust_df)} rows")

    # 2. Stores
    store_df = clean_stores(pd.read_csv(RAW_DIR / "stores.csv"))
    store_df.to_csv(PROCESSED_DIR / "stores.csv", index=False)
    print(f"  Cleaned stores: {len(store_df)} rows")

    # 3. Products
    prod_df = clean_products(pd.read_csv(RAW_DIR / "products.csv"))
    prod_df.to_csv(PROCESSED_DIR / "products.csv", index=False)
    print(f"  Cleaned products: {len(prod_df)} rows")

    # 4. Orders (must reference existing customers and stores)
    ord_df = clean_orders(pd.read_csv(RAW_DIR / "orders.csv"))
    valid_cids = set(cust_df["Customer_Id"])
    valid_sids = set(store_df["store_id"])
    ord_df = ord_df[ord_df["Customer_id"].isin(valid_cids) & ord_df["store_id"].isin(valid_sids)]
    ord_df.to_csv(PROCESSED_DIR / "orders.csv", index=False)
    print(f"  Cleaned orders: {len(ord_df)} rows")

    # 5. Order Items (must reference existing orders and products)
    item_df = clean_order_items(pd.read_csv(RAW_DIR / "order_items.csv"))
    valid_oids = set(ord_df["order_id"])
    valid_pids = set(prod_df["product_id"])
    item_df = item_df[item_df["order_id"].isin(valid_oids) & item_df["product_id"].isin(valid_pids)]
    item_df.to_csv(PROCESSED_DIR / "order_items.csv", index=False)
    print(f"  Cleaned order_items: {len(item_df)} rows")

    # 6. Inventory (must reference existing stores and products)
    inv_df = clean_inventory(pd.read_csv(RAW_DIR / "inventory.csv"))
    inv_df = inv_df[inv_df["store_id"].isin(valid_sids) & inv_df["product_id"].isin(valid_pids)]
    inv_df.to_csv(PROCESSED_DIR / "inventory.csv", index=False)
    print(f"  Cleaned inventory: {len(inv_df)} rows")

    print("\nAll cleaned CSVs saved to data/processed/")


if __name__ == "__main__":
    run_cleaning()
