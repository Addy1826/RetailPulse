# test_pipeline.py - Tests for RetailPulse pipeline and analytics

import sys
from pathlib import Path
import pandas as pd
import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from src.cleaning import (
    clean_customers, clean_stores, clean_products,
    clean_orders, clean_order_items, clean_inventory
)
from src.validation import validate_all_data
from src.database import run_query
import src.analytics as analytics

RAW_DIR = PROJECT_ROOT / "data" / "raw"
PROCESSED_DIR = PROJECT_ROOT / "data" / "processed"


class TestDataGeneration:
    """Verify raw CSV files exist and have data."""

    @pytest.mark.parametrize("filename,min_rows", [
        ("Customers.csv", 100),
        ("stores.csv", 5),
        ("products.csv", 10),
        ("orders.csv", 500),
        ("order_items.csv", 1000),
        ("inventory.csv", 50),
    ])
    def test_csv_exists_and_has_rows(self, filename, min_rows):
        path = RAW_DIR / filename
        assert path.exists(), f"{filename} is missing"
        df = pd.read_csv(path)
        assert len(df) >= min_rows, f"{filename} has fewer rows than expected"


class TestCleaning:
    """Verify cleaning logic handles duplicates and values correctly."""

    def test_customers_cleaning(self):
        df = pd.DataFrame({
            "Customer_Id": [1, 1, 2],
            "Customer_name": [" Alice ", "Alice", "Bob"],
            "email": ["alice@test.com", "alice@test.com", "bob@test.com"],
            "city": ["Mumbai", "Mumbai", "Delhi"],
            "signup_date": ["2026-01-01", "2026-01-01", "2026-01-02"]
        })
        cleaned = clean_customers(df)
        assert len(cleaned) == 2
        assert cleaned["Customer_name"].iloc[0] == "Alice"

    def test_products_positive_price(self):
        df = pd.DataFrame({
            "product_id": [1, 2],
            "product_name": ["Phone", "Bad"],
            "category": ["Electronics", "Electronics"],
            "Unit_price": [1000.0, -50.0],
            "recorder_level": [10, 10]
        })
        cleaned = clean_products(df)
        assert len(cleaned) == 1
        assert cleaned["product_id"].iloc[0] == 1

    def test_order_items_positive_quantity(self):
        df = pd.DataFrame({
            "order_id": [1, 2],
            "product_id": [1, 1],
            "quantity": [2, 0],
            "selling_price": [500.0, 500.0]
        })
        cleaned = clean_order_items(df)
        assert len(cleaned) == 1


class TestValidation:
    """Verify validation passes on processed data."""

    def test_validation_passes(self):
        cust = pd.read_csv(PROCESSED_DIR / "Customers.csv")
        stores = pd.read_csv(PROCESSED_DIR / "stores.csv")
        prods = pd.read_csv(PROCESSED_DIR / "products.csv")
        orders = pd.read_csv(PROCESSED_DIR / "orders.csv")
        items = pd.read_csv(PROCESSED_DIR / "order_items.csv")
        inv = pd.read_csv(PROCESSED_DIR / "inventory.csv")
        assert validate_all_data(cust, stores, prods, orders, items, inv) is True


class TestDatabase:
    """Verify tables exist and have data in MySQL."""

    @pytest.mark.parametrize("table,min_rows", [
        ("Customers", 100),
        ("stores", 5),
        ("products", 10),
        ("orders", 500),
        ("order_items", 1000),
        ("inventory", 50),
    ])
    def test_database_tables_have_rows(self, table, min_rows):
        df = run_query(f"SELECT COUNT(*) AS c FROM {table}")
        assert int(df["c"].iloc[0]) >= min_rows


class TestAnalytics:
    """Verify analytics queries return valid results."""

    def test_kpis(self):
        kpis = analytics.get_revenue_kpis()
        assert kpis["total_orders"] > 0
        assert kpis["total_revenue"] > 0

    def test_monthly_revenue(self):
        df = analytics.get_monthly_revenue()
        assert not df.empty
        assert "revenue" in df.columns

    def test_top_products(self):
        df = analytics.get_top_products(5)
        assert len(df) <= 5
        assert "product_name" in df.columns

    def test_low_stock_alerts(self):
        df = analytics.get_low_stock_alerts()
        assert "qty_on_hand" in df.columns
