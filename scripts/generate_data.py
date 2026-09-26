# generate_data.py - Creates fake retail data as CSVs
# Adds some messy data on purpose so cleaning has something to fix

import csv
import random
from datetime import datetime, timedelta
from pathlib import Path

import numpy as np
from faker import Faker

fake = Faker("en_IN")
Faker.seed(42)
random.seed(42)
np.random.seed(42)

RAW_DIR = Path(__file__).resolve().parents[1] / "data" / "raw"
RAW_DIR.mkdir(parents=True, exist_ok=True)

# How much data to generate
N_CUSTOMERS = 500
N_CATEGORIES = 10
N_PRODUCTS = 120
N_STORES = 15
N_ORDERS = 5000
MAX_ITEMS = 5

# Indian cities and states
STATES_CITIES = {
    "Maharashtra":   ["Mumbai", "Pune", "Nagpur"],
    "Karnataka":     ["Bengaluru", "Mysuru", "Hubli"],
    "Delhi":         ["New Delhi"],
    "Tamil Nadu":    ["Chennai", "Coimbatore"],
    "Telangana":     ["Hyderabad", "Warangal"],
    "West Bengal":   ["Kolkata", "Howrah"],
    "Gujarat":       ["Ahmedabad", "Surat", "Vadodara"],
    "Uttar Pradesh": ["Lucknow", "Noida", "Kanpur"],
    "Rajasthan":     ["Jaipur", "Udaipur"],
    "Kerala":        ["Kochi", "Thiruvananthapuram"],
}

REGIONS_MAP = {
    "Maharashtra": "West", "Gujarat": "West", "Rajasthan": "West",
    "Karnataka": "South", "Tamil Nadu": "South", "Telangana": "South", "Kerala": "South",
    "Delhi": "North", "Uttar Pradesh": "North",
    "West Bengal": "East",
}

CATEGORIES = [
    ("Electronics",     "Phones, laptops, tablets, accessories"),
    ("Clothing",        "Men's, women's, and kids' apparel"),
    ("Footwear",        "Shoes, sandals, sneakers"),
    ("Home & Kitchen",  "Cookware, decor, furnishings"),
    ("Beauty & Health", "Skincare, haircare, supplements"),
    ("Sports & Fitness","Equipment, sportswear, yoga"),
    ("Books",           "Fiction, non-fiction, academic"),
    ("Toys & Games",    "Board games, puzzles, action figures"),
    ("Grocery",         "Staples, snacks, beverages"),
    ("Stationery",      "Notebooks, pens, art supplies"),
]

BRANDS = {
    "Electronics":      ["Samsung", "Apple", "OnePlus", "boAt", "Realme"],
    "Clothing":         ["Levi's", "Allen Solly", "H&M", "Zara", "FabIndia"],
    "Footwear":         ["Nike", "Adidas", "Bata", "Puma", "Woodland"],
    "Home & Kitchen":   ["Prestige", "Philips", "Milton", "Borosil", "IKEA"],
    "Beauty & Health":  ["Lakme", "Nivea", "Himalaya", "Mamaearth", "WOW"],
    "Sports & Fitness": ["Decathlon", "Nivia", "Yonex", "Cosco", "Boldfit"],
    "Books":            ["Penguin", "HarperCollins", "Rupa", "Scholastic", "Oxford"],
    "Toys & Games":     ["Funskool", "Lego", "Mattel", "Hasbro", "Toyzone"],
    "Grocery":          ["Tata", "Amul", "Fortune", "Haldiram", "MTR"],
    "Stationery":       ["Classmate", "Cello", "Faber-Castell", "Pilot", "Camlin"],
}

PAYMENT_METHODS = ["Credit Card", "Debit Card", "UPI", "Cash", "Wallet"]
SEGMENTS = ["Regular", "Premium", "VIP"]
STORE_TYPES = ["Flagship", "Mall", "Outlet", "Online"]
ORDER_STATUSES = ["Completed", "Returned", "Cancelled"]


def make_dirty(value, prob=0.03):
    """Randomly corrupt a value to simulate messy data."""
    if random.random() < prob:
        return random.choice([None, "", "N/A", "  "])
    return value


def make_outlier_price(base, prob=0.02):
    """Occasionally return an unrealistic price."""
    if random.random() < prob:
        return round(base * random.uniform(10, 50), 2)
    return base


def generate_customers():
    rows = []
    for i in range(1, N_CUSTOMERS + 1):
        state = random.choice(list(STATES_CITIES))
        city = random.choice(STATES_CITIES[state])
        rows.append({
            "customer_id": i,
            "first_name": make_dirty(fake.first_name()),
            "last_name": fake.last_name(),
            "email": fake.ascii_email(),
            "phone": make_dirty(fake.phone_number()),
            "city": city,
            "state": state,
            "join_date": fake.date_between("-3y", "today").isoformat(),
            "segment": random.choice(SEGMENTS),
        })
    # Add some duplicate rows on purpose
    for _ in range(int(N_CUSTOMERS * 0.02)):
        dup = random.choice(rows).copy()
        dup["customer_id"] = len(rows) + 1
        rows.append(dup)
    return rows


def generate_categories():
    return [
        {"category_id": i + 1, "category_name": name, "description": desc}
        for i, (name, desc) in enumerate(CATEGORIES)
    ]


def generate_products(categories):
    rows = []
    for i in range(1, N_PRODUCTS + 1):
        cat = random.choice(categories)
        cat_name = cat["category_name"]
        base_price = round(random.uniform(99, 9999), 2)
        cost = round(base_price * random.uniform(0.4, 0.75), 2)
        rows.append({
            "product_id": i,
            "product_name": f"{random.choice(BRANDS[cat_name])} {fake.word().title()} {fake.word().title()}",
            "category_id": cat["category_id"],
            "brand": random.choice(BRANDS[cat_name]),
            "unit_price": make_outlier_price(base_price),
            "cost_price": cost,
            "sku": f"SKU-{i:05d}",
            "is_active": random.choices([1, 0], weights=[95, 5])[0],
        })
    return rows


def generate_stores():
    rows = []
    for i in range(1, N_STORES + 1):
        state = random.choice(list(STATES_CITIES))
        city = random.choice(STATES_CITIES[state])
        rows.append({
            "store_id": i,
            "store_name": f"RetailPulse {city} {random.choice(STORE_TYPES)}",
            "city": city,
            "state": state,
            "region": REGIONS_MAP[state],
            "store_type": random.choice(STORE_TYPES),
            "open_date": fake.date_between("-5y", "-1y").isoformat(),
        })
    return rows


def generate_orders_and_items(customers, stores, products):
    orders, items = [], []
    item_id = 1
    cust_ids = [c["customer_id"] for c in customers]
    store_ids = [s["store_id"] for s in stores]

    for oid in range(1, N_ORDERS + 1):
        odate = fake.date_time_between("-2y", "now")
        status = random.choices(ORDER_STATUSES, weights=[85, 10, 5])[0]

        order = {
            "order_id": oid,
            "customer_id": random.choice(cust_ids),
            "store_id": random.choice(store_ids),
            "order_date": odate.strftime("%Y-%m-%d %H:%M:%S"),
            "status": make_dirty(status, prob=0.01),
            "payment_method": random.choice(PAYMENT_METHODS),
            "total_amount": 0.0,
        }

        n_items = random.randint(1, MAX_ITEMS)
        order_total = 0.0

        for _ in range(n_items):
            prod = random.choice(products)
            qty = random.randint(1, 4)
            disc = round(random.choice([0, 0, 0, 5, 10, 15, 20, 25]), 2)
            up = float(prod["unit_price"])
            line = round(qty * up * (1 - disc / 100), 2)

            items.append({
                "item_id": item_id,
                "order_id": oid,
                "product_id": prod["product_id"],
                "quantity": make_dirty(qty, prob=0.01),
                "unit_price": up,
                "discount_pct": disc,
            })
            order_total += line
            item_id += 1

        order["total_amount"] = round(order_total, 2)
        orders.append(order)

    # Add a few duplicate orders
    for _ in range(int(N_ORDERS * 0.01)):
        dup = random.choice(orders).copy()
        dup["order_id"] = len(orders) + 1
        orders.append(dup)

    return orders, items


def generate_inventory(stores, products):
    rows = []
    inv_id = 1
    for s in stores:
        subset = random.sample(products, k=random.randint(40, len(products)))
        for p in subset:
            rows.append({
                "inventory_id": inv_id,
                "store_id": s["store_id"],
                "product_id": p["product_id"],
                "qty_on_hand": random.randint(0, 200),
                "reorder_level": random.choice([5, 10, 15, 20, 25]),
                "last_restock": make_dirty(
                    fake.date_between("-6m", "today").isoformat(), prob=0.05
                ),
            })
            inv_id += 1
    return rows


def write_csv(rows, filename):
    path = RAW_DIR / filename
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=rows[0].keys())
        writer.writeheader()
        writer.writerows(rows)
    print(f"  Saved {filename} ({len(rows)} rows)")
    return path


if __name__ == "__main__":
    print("Generating raw data...")
    print()

    customers = generate_customers()
    categories = generate_categories()
    products = generate_products(categories)
    stores = generate_stores()
    orders, items = generate_orders_and_items(customers, stores, products)
    inventory = generate_inventory(stores, products)

    write_csv(customers,  "customers.csv")
    write_csv(categories, "categories.csv")
    write_csv(products,   "products.csv")
    write_csv(stores,     "stores.csv")
    write_csv(orders,     "orders.csv")
    write_csv(items,      "order_items.csv")
    write_csv(inventory,  "inventory.csv")

    print()
    print("Done! Raw CSVs saved to data/raw/")
