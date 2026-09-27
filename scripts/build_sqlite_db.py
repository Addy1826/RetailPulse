# build_sqlite_db.py - Builds SQLite database for local fallback / cloud deployment

import sqlite3
from pathlib import Path
import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DB_PATH = PROJECT_ROOT / "data" / "retailpulse.db"
PROCESSED_DIR = PROJECT_ROOT / "data" / "processed"

if DB_PATH.exists():
    DB_PATH.unlink()

conn = sqlite3.connect(DB_PATH)

# Schema matching the user's 6 tables
conn.executescript("""
CREATE TABLE Customers (
    Customer_Id INTEGER PRIMARY KEY,
    Customer_name TEXT NOT NULL,
    email TEXT UNIQUE,
    city TEXT,
    signup_date TEXT
);

CREATE TABLE stores (
    store_id INTEGER PRIMARY KEY,
    store_name TEXT NOT NULL,
    city TEXT NOT NULL,
    opening_date TEXT
);

CREATE TABLE products (
    product_id INTEGER PRIMARY KEY,
    product_name TEXT NOT NULL,
    category TEXT NOT NULL,
    Unit_price REAL CHECK(Unit_price > 0),
    reorder_level INTEGER DEFAULT 10
);

CREATE TABLE orders (
    order_id INTEGER PRIMARY KEY,
    Customer_id INTEGER NOT NULL,
    store_id INTEGER NOT NULL,
    Order_date TEXT NOT NULL,
    payment_method TEXT,
    order_status TEXT,
    FOREIGN KEY (Customer_id) REFERENCES Customers (Customer_Id),
    FOREIGN KEY (store_id) REFERENCES stores (store_id)
);

CREATE TABLE order_items (
    order_id INTEGER,
    product_id INTEGER,
    quantity INTEGER CHECK (quantity > 0),
    selling_price REAL CHECK (selling_price > 0),
    PRIMARY KEY (order_id, product_id),
    FOREIGN KEY (order_id) REFERENCES orders (order_id),
    FOREIGN KEY (product_id) REFERENCES products (product_id)
);

CREATE TABLE inventory (
    store_id INTEGER,
    product_id INTEGER,
    stock_quantity INTEGER CHECK (stock_quantity >= 0),
    last_updated TEXT,
    PRIMARY KEY (store_id, product_id),
    FOREIGN KEY (store_id) REFERENCES stores (store_id),
    FOREIGN KEY (product_id) REFERENCES products (product_id)
);
""")

tables = [
    ("Customers", "Customers.csv"),
    ("stores", "stores.csv"),
    ("products", "products.csv"),
    ("orders", "orders.csv"),
    ("order_items", "order_items.csv"),
    ("inventory", "inventory.csv"),
]

for table_name, csv_name in tables:
    csv_file = PROCESSED_DIR / csv_name
    if csv_file.exists():
        df = pd.read_csv(csv_file)
        df.to_sql(table_name, conn, if_exists="append", index=False)
        print(f"Loaded {table_name}: {len(df)} rows")

conn.commit()
conn.close()

print(f"\nSQLite database created at {DB_PATH}, size: {DB_PATH.stat().st_size / 1024:.1f} KB")
