# generate_data.py - Creates sample data for RetailPulse
# Tables: Customers, stores, products, orders, order_items, inventory

import csv
import random
from datetime import datetime, timedelta
from pathlib import Path
from faker import Faker

fake = Faker("en_IN")
random.seed(42)

PROJECT_ROOT = Path(__file__).resolve().parents[1]
RAW_DIR = PROJECT_ROOT / "data" / "raw"
RAW_DIR.mkdir(parents=True, exist_ok=True)

# Common Indian cities
CITIES = ["Mumbai", "Delhi", "Bengaluru", "Hyderabad", "Chennai", "Kolkata", "Pune", "Ahmedabad", "Jaipur", "Lucknow"]

# Categories and sample products
CATEGORIES = {
    "Electronics": ["Smartphone", "Wireless Earbuds", "Laptop", "Smartwatch", "Bluetooth Speaker", "Tablet", "Power Bank"],
    "Clothing": ["Cotton T-Shirt", "Slim Fit Jeans", "Denim Jacket", "Formal Shirt", "Ethnic Kurta", "Hoodie", "Track Pants"],
    "Footwear": ["Running Shoes", "Leather Formal Shoes", "Casual Sneakers", "Sports Sandals", "Slip-on Loafers"],
    "Home & Kitchen": ["Mixer Grinder", "Non-Stick Cookware Set", "Water Purifier", "Electric Kettle", "Stainless Steel Bottle"],
    "Groceries": ["Organic Green Tea", "Almonds 500g", "Basmati Rice 5kg", "Virgin Olive Oil", "Dark Chocolate Bar"]
}

PAYMENT_METHODS = ["UPI", "Credit Card", "Debit Card", "Cash", "Net Banking"]
ORDER_STATUSES = ["Completed", "Completed", "Completed", "Completed", "Cancelled", "Returned"]


def generate_customers(n=500):
    rows = []
    for cid in range(1, n + 1):
        name = fake.name()
        email = f"{name.lower().replace(' ', '.')}_{cid}@example.com"
        city = random.choice(CITIES)
        days_ago = random.randint(30, 730)
        signup_date = (datetime.now() - timedelta(days=days_ago)).strftime("%Y-%m-%d")
        rows.append({
            "Customer_Id": cid,
            "Customer_name": name,
            "email": email,
            "city": city,
            "signup_date": signup_date
        })
    return rows


def generate_stores(n=10):
    rows = []
    for sid in range(1, n + 1):
        city = CITIES[sid - 1] if sid <= len(CITIES) else random.choice(CITIES)
        name = f"RetailPulse {city} Central"
        days_ago = random.randint(100, 1000)
        open_date = (datetime.now() - timedelta(days=days_ago)).strftime("%Y-%m-%d")
        rows.append({
            "store_id": sid,
            "store_name": name,
            "city": city,
            "openinig_date": open_date
        })
    return rows


def generate_products():
    rows = []
    pid = 1
    for cat, items in CATEGORIES.items():
        for item in items:
            unit_price = round(random.uniform(200, 15000), 2)
            rows.append({
                "product_id": pid,
                "product_name": item,
                "category": cat,
                "Unit_price": unit_price,
                "recorder_level": random.randint(10, 30)
            })
            pid += 1
    return rows


def generate_orders(num_orders=3000, num_customers=500, num_stores=10):
    rows = []
    for oid in range(1, num_orders + 1):
        cid = random.randint(1, num_customers)
        sid = random.randint(1, num_stores)
        days_ago = random.randint(1, 365)
        order_date = (datetime.now() - timedelta(days=days_ago)).strftime("%Y-%m-%d")
        pay_method = random.choice(PAYMENT_METHODS)
        status = random.choice(ORDER_STATUSES)
        rows.append({
            "order_id": oid,
            "Customer_id": cid,
            "store_id": sid,
            "Order_date": order_date,
            "payment_method": pay_method,
            "order_status": status
        })
    return rows


def generate_order_items(orders, products):
    rows = []
    prod_dict = {p["product_id"]: p["Unit_price"] for p in products}
    prod_ids = list(prod_dict.keys())

    for ord_row in orders:
        oid = ord_row["order_id"]
        # 1 to 4 distinct items per order
        num_items = random.randint(1, 4)
        chosen_prods = random.sample(prod_ids, num_items)
        for pid in chosen_prods:
            qty = random.randint(1, 5)
            # Selling price with small markup or discount
            base_price = prod_dict[pid]
            selling_price = round(base_price * random.uniform(0.9, 1.25), 2)
            rows.append({
                "order_id": oid,
                "product_id": pid,
                "quantity": qty,
                "selling_price": selling_price
            })
    return rows


def generate_inventory(stores, products):
    rows = []
    for s in stores:
        sid = s["store_id"]
        for p in products:
            pid = p["product_id"]
            qty = random.randint(0, 100)
            days_ago = random.randint(1, 45)
            last_up = (datetime.now() - timedelta(days=days_ago)).strftime("%Y-%m-%d")
            rows.append({
                "store_id": sid,
                "product_id": pid,
                "stock_quantity": qty,
                "last_updated": last_up
            })
    return rows


def save_csv(data, filename):
    filepath = RAW_DIR / filename
    if not data:
        return
    with open(filepath, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=data[0].keys())
        writer.writeheader()
        writer.writerows(data)
    print(f"Generated {filename}: {len(data)} rows")


if __name__ == "__main__":
    print("Generating raw retail data...")
    customers = generate_customers(500)
    stores = generate_stores(10)
    products = generate_products()
    orders = generate_orders(3000, len(customers), len(stores))
    order_items = generate_order_items(orders, products)
    inventory = generate_inventory(stores, products)

    save_csv(customers, "Customers.csv")
    save_csv(stores, "stores.csv")
    save_csv(products, "products.csv")
    save_csv(orders, "orders.csv")
    save_csv(order_items, "order_items.csv")
    save_csv(inventory, "inventory.csv")
    print("Done generating raw data!")
