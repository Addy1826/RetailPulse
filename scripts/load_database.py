# load_database.py - Loads cleaned CSVs into MySQL

import sys
from pathlib import Path
import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from src.database import load_dataframe, run_script

PROCESSED_DIR = PROJECT_ROOT / "data" / "processed"
SCHEMA_SQL = PROJECT_ROOT / "sql" / "schema.sql"

# Order matters because of foreign keys
TABLES = [
    ("Customers", "Customers.csv"),
    ("stores", "stores.csv"),
    ("products", "products.csv"),
    ("orders", "orders.csv"),
    ("order_items", "order_items.csv"),
    ("inventory", "inventory.csv"),
]


def load_all():
    print("Applying schema to MySQL...")
    run_script(SCHEMA_SQL)
    print("Schema applied successfully.\n")

    print("Loading data into MySQL tables...")
    for table_name, csv_name in TABLES:
        csv_path = PROCESSED_DIR / csv_name
        if not csv_path.exists():
            print(f"Error: {csv_path} not found.")
            sys.exit(1)

        df = pd.read_csv(csv_path)

        # Parse date columns
        for col in df.columns:
            if "date" in col.lower():
                df[col] = pd.to_datetime(df[col], errors="coerce")

        load_dataframe(df, table_name, if_exists="append")
        print(f"  Loaded {table_name}: {len(df)} rows")

    print("\nAll data loaded into MySQL successfully!")


if __name__ == "__main__":
    load_all()
