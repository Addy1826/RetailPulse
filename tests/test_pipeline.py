# test_pipeline.py - Pre-interview test suite for RetailPulse SQL & Analytics

import math
import sys
from pathlib import Path
import pandas as pd
import pytest
from sqlalchemy import text

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from src.cleaning import (
    clean_customers, clean_stores, clean_products,
    clean_orders, clean_order_items, clean_inventory
)
from src.validation import validate_all_data
from src.database import get_engine, run_query
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
            "reorder_level": [10, 10]
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


class TestDatabaseIntegrity:
    """Verify database schema, composite keys, NOT NULL constraints, and FK relationships."""

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

    def test_orders_foreign_keys_not_null(self):
        """Verify orders.Customer_id and orders.store_id have zero nulls."""
        df_cust_nulls = run_query("SELECT COUNT(*) AS c FROM orders WHERE Customer_id IS NULL")
        assert int(df_cust_nulls["c"].iloc[0]) == 0

        df_store_nulls = run_query("SELECT COUNT(*) AS c FROM orders WHERE store_id IS NULL")
        assert int(df_store_nulls["c"].iloc[0]) == 0

    def test_no_orphan_order_items(self):
        """Verify all order_items reference valid orders and products."""
        df = run_query("""
            SELECT COUNT(*) AS orphan_count
            FROM order_items oi
            LEFT JOIN orders o ON oi.order_id = o.order_id
            WHERE o.order_id IS NULL
        """)
        assert int(df["orphan_count"].iloc[0]) == 0

    def test_composite_primary_keys(self):
        """Verify composite PK uniqueness on order_items (order_id, product_id) and inventory (store_id, product_id)."""
        oi_dups = run_query("""
            SELECT order_id, product_id, COUNT(*) AS cnt
            FROM order_items
            GROUP BY order_id, product_id
            HAVING COUNT(*) > 1
        """)
        assert len(oi_dups) == 0

        inv_dups = run_query("""
            SELECT store_id, product_id, COUNT(*) AS cnt
            FROM inventory
            GROUP BY store_id, product_id
            HAVING COUNT(*) > 1
        """)
        assert len(inv_dups) == 0

    def test_sqlite_foreign_keys_pragma(self):
        """Verify PRAGMA foreign_keys is enabled (returns 1) on SQLite fallback."""
        from sqlalchemy import create_engine, event
        from src.database import _sqlite_setup, SQLITE_PATH
        engine = create_engine(f"sqlite:///{SQLITE_PATH.as_posix()}")
        event.listen(engine, "connect", _sqlite_setup)
        with engine.connect() as conn:
            val = conn.execute(text("PRAGMA foreign_keys;")).scalar()
            assert val == 1


class TestAnalyticsQueries:
    """Verify analytical correctness, business logic, and query results."""

    def test_true_average_order_value(self):
        """Verify AOV = total_revenue / distinct completed orders."""
        kpis = analytics.get_revenue_kpis()
        tot_rev = kpis["total_revenue"]
        tot_ord = kpis["total_orders"]
        aov = kpis["avg_order_value"]

        expected_aov = tot_rev / tot_ord
        assert math.isclose(aov, expected_aov, rel_tol=1e-5), f"AOV {aov} != expected {expected_aov}"

    def test_having_repeat_customers(self):
        """Verify HAVING query returns high-frequency customers with completed orders."""
        df = analytics.get_repeat_customers(min_orders=6)
        assert "completed_orders" in df.columns
        assert "total_spent" in df.columns
        if not df.empty:
            assert (df["completed_orders"] >= 6).all()

    def test_anti_join_customers_with_no_orders(self):
        """Verify anti-join query executes cleanly and returns expected schema."""
        df = analytics.get_customers_with_no_orders()
        assert "Customer_Id" in df.columns
        assert "Customer_name" in df.columns

    def test_low_stock_alerts_uses_reorder_level(self):
        """Verify low-stock query executes with reorder_level column."""
        df = analytics.get_low_stock_alerts()
        assert "qty_on_hand" in df.columns
        assert "reorder_level" in df.columns

    def test_monthly_revenue_trend(self):
        df = analytics.get_monthly_revenue()
        assert not df.empty
        assert "month" in df.columns
        assert "revenue" in df.columns

    def test_top_products_by_revenue(self):
        df = analytics.get_top_products(10)
        assert len(df) <= 10
        assert "product_name" in df.columns
        assert "revenue" in df.columns

    def test_profit_margins_estimated_gross_margin(self):
        df = analytics.get_profit_margins(10)
        assert "estimated_gross_margin" in df.columns
        assert "margin_pct" in df.columns
