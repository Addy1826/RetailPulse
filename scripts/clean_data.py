# clean_data.py - Reads raw CSVs, cleans them, validates, and saves to data/processed/

import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.cleaning import (
    clean_categories, clean_customers, clean_inventory,
    clean_order_items, clean_orders, clean_products, clean_stores,
)
from src.validation import run_all_validations

RAW_DIR = Path(__file__).resolve().parents[1] / "data" / "raw"
PROCESSED_DIR = Path(__file__).resolve().parents[1] / "data" / "processed"
PROCESSED_DIR.mkdir(parents=True, exist_ok=True)


def load_raw(name):
    path = RAW_DIR / f"{name}.csv"
    if not path.exists():
        print(f"  ERROR: {path} not found. Run generate_data.py first.")
        sys.exit(1)
    return pd.read_csv(path)


if __name__ == "__main__":
    print("Loading raw data...")

    raw = {
        "customers":   load_raw("customers"),
        "categories":  load_raw("categories"),
        "products":    load_raw("products"),
        "stores":      load_raw("stores"),
        "orders":      load_raw("orders"),
        "order_items": load_raw("order_items"),
        "inventory":   load_raw("inventory"),
    }

    for name, df in raw.items():
        print(f"  Raw {name}: {len(df)} rows")

    # Clean each table
    print()
    print("Cleaning...")

    cleaned = {
        "customers":   clean_customers(raw["customers"]),
        "categories":  clean_categories(raw["categories"]),
        "products":    clean_products(raw["products"]),
        "stores":      clean_stores(raw["stores"]),
        "orders":      clean_orders(raw["orders"]),
        "order_items": clean_order_items(raw["order_items"]),
        "inventory":   clean_inventory(raw["inventory"]),
    }

    # Filter out rows with invalid foreign keys
    valid_order_ids = set(cleaned["orders"]["order_id"])
    valid_product_ids = set(cleaned["products"]["product_id"])
    valid_store_ids = set(cleaned["stores"]["store_id"])
    valid_customer_ids = set(cleaned["customers"]["customer_id"])

    cleaned["orders"] = cleaned["orders"][
        cleaned["orders"]["customer_id"].isin(valid_customer_ids)
        & cleaned["orders"]["store_id"].isin(valid_store_ids)
    ]
    valid_order_ids = set(cleaned["orders"]["order_id"])

    cleaned["order_items"] = cleaned["order_items"][
        cleaned["order_items"]["order_id"].isin(valid_order_ids)
        & cleaned["order_items"]["product_id"].isin(valid_product_ids)
    ]
    cleaned["inventory"] = cleaned["inventory"][
        cleaned["inventory"]["store_id"].isin(valid_store_ids)
        & cleaned["inventory"]["product_id"].isin(valid_product_ids)
    ]

    # Reset IDs
    cleaned["order_items"] = cleaned["order_items"].reset_index(drop=True)
    cleaned["order_items"]["item_id"] = range(1, len(cleaned["order_items"]) + 1)

    cleaned["inventory"] = cleaned["inventory"].reset_index(drop=True)
    cleaned["inventory"]["inventory_id"] = range(1, len(cleaned["inventory"]) + 1)

    for name, df in cleaned.items():
        print(f"  Cleaned {name}: {len(df)} rows")

    # Validate
    print()
    print("Validating...")

    results = run_all_validations(
        cleaned["customers"], cleaned["categories"], cleaned["products"],
        cleaned["stores"], cleaned["orders"], cleaned["order_items"],
        cleaned["inventory"],
    )

    all_ok = True
    for table, issues in results.items():
        if issues:
            all_ok = False
            for iss in issues:
                print(f"  WARNING: {iss}")
        else:
            print(f"  {table} - OK")

    # Save cleaned CSVs
    print()
    for name, df in cleaned.items():
        out_path = PROCESSED_DIR / f"{name}.csv"
        df.to_csv(out_path, index=False)

    print("Done! Cleaned CSVs saved to data/processed/")
