import sqlite3
from pathlib import Path
import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DB_PATH = PROJECT_ROOT / "data" / "retailpulse.db"
PROCESSED_DIR = PROJECT_ROOT / "data" / "processed"

if DB_PATH.exists():
    DB_PATH.unlink()

conn = sqlite3.connect(DB_PATH)

# Schema matching the actual processed data
conn.executescript("""
CREATE TABLE IF NOT EXISTS categories (
    category_id INTEGER PRIMARY KEY,
    category_name TEXT NOT NULL,
    description TEXT
);

CREATE TABLE IF NOT EXISTS customers (
    customer_id INTEGER PRIMARY KEY,
    first_name TEXT NOT NULL,
    last_name TEXT NOT NULL,
    email TEXT UNIQUE,
    phone TEXT,
    city TEXT,
    state TEXT,
    join_date TEXT NOT NULL,
    segment TEXT DEFAULT 'Regular'
);

CREATE TABLE IF NOT EXISTS products (
    product_id INTEGER PRIMARY KEY,
    product_name TEXT NOT NULL,
    category_id INTEGER,
    brand TEXT,
    unit_price REAL NOT NULL,
    cost_price REAL NOT NULL,
    sku TEXT UNIQUE,
    is_active INTEGER DEFAULT 1,
    FOREIGN KEY (category_id) REFERENCES categories (category_id)
);

CREATE TABLE IF NOT EXISTS stores (
    store_id INTEGER PRIMARY KEY,
    store_name TEXT NOT NULL,
    city TEXT NOT NULL,
    state TEXT NOT NULL,
    region TEXT NOT NULL,
    store_type TEXT NOT NULL,
    open_date TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS orders (
    order_id INTEGER PRIMARY KEY,
    customer_id INTEGER NOT NULL,
    store_id INTEGER NOT NULL,
    order_date TEXT NOT NULL,
    status TEXT DEFAULT 'Completed',
    payment_method TEXT NOT NULL,
    total_amount REAL DEFAULT 0.00,
    FOREIGN KEY (customer_id) REFERENCES customers (customer_id),
    FOREIGN KEY (store_id) REFERENCES stores (store_id)
);

CREATE TABLE IF NOT EXISTS order_items (
    item_id INTEGER PRIMARY KEY,
    order_id INTEGER NOT NULL,
    product_id INTEGER NOT NULL,
    quantity INTEGER NOT NULL,
    unit_price REAL NOT NULL,
    discount_pct REAL DEFAULT 0.00,
    line_total REAL GENERATED ALWAYS AS (quantity * unit_price * (1 - (discount_pct / 100.0))) STORED,
    FOREIGN KEY (order_id) REFERENCES orders (order_id),
    FOREIGN KEY (product_id) REFERENCES products (product_id)
);

CREATE TABLE IF NOT EXISTS inventory (
    inventory_id INTEGER PRIMARY KEY,
    store_id INTEGER NOT NULL,
    product_id INTEGER NOT NULL,
    qty_on_hand INTEGER DEFAULT 0,
    reorder_level INTEGER DEFAULT 10,
    last_restock TEXT,
    FOREIGN KEY (store_id) REFERENCES stores (store_id),
    FOREIGN KEY (product_id) REFERENCES products (product_id)
);
""")

tables = ['categories', 'customers', 'products', 'stores', 'orders', 'order_items', 'inventory']
for t in tables:
    csv_file = PROCESSED_DIR / f"{t}.csv"
    if csv_file.exists():
        df = pd.read_csv(csv_file)
        df.to_sql(t, conn, if_exists="append", index=False)
        print(f"Loaded {t}: {len(df)} rows")

conn.commit()
conn.close()

print(f"Database created at {DB_PATH}, size: {DB_PATH.stat().st_size / 1024:.1f} KB")
