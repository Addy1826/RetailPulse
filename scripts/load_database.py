# load_database.py - Loads cleaned CSVs into MySQL

import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.database import get_engine, load_dataframe, run_script

PROJECT_ROOT = Path(__file__).resolve().parents[1]
PROCESSED_DIR = PROJECT_ROOT / "data" / "processed"
SCHEMA_SQL = PROJECT_ROOT / "sql" / "schema.sql"

# Order matters because of foreign keys
TABLES = [
    "customers", "categories", "products", "stores",
    "orders", "order_items", "inventory",
]

# Columns that MySQL generates automatically
SKIP_COLS = {
    "order_items": ["line_total"],
}


if __name__ == "__main__":
    print("Applying database schema...")
    run_script(SCHEMA_SQL)
    print("  Schema applied")
    print()

    print("Loading data into MySQL...")
    for table in TABLES:
        csv_path = PROCESSED_DIR / f"{table}.csv"
        if not csv_path.exists():
            print(f"  ERROR: {csv_path} not found. Run clean_data.py first.")
            sys.exit(1)

        df = pd.read_csv(csv_path)

        # Drop columns that the database generates
        for col in SKIP_COLS.get(table, []):
            if col in df.columns:
                df = df.drop(columns=[col])

        # Convert date columns
        for col in df.columns:
            if "date" in col.lower():
                df[col] = pd.to_datetime(df[col], errors="coerce")

        load_dataframe(df, table, if_exists="append")
        print(f"  {table}: {len(df)} rows loaded")

    print()
    print("Done! All tables loaded into MySQL.")
