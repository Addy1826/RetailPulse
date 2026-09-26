# tests/test_pipeline.py
# End-to-end tests for the RetailPulse data pipeline.

import sys
from pathlib import Path

import pandas as pd
import pytest

# Ensure project root is on the path.
PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from src.cleaning import (
    clean_categories,
    clean_customers,
    clean_inventory,
    clean_order_items,
    clean_orders,
    clean_products,
    clean_stores,
)
from src.database import get_engine, run_query
from src.validation import run_all_validations

RAW_DIR       = PROJECT_ROOT / "data" / "raw"
PROCESSED_DIR = PROJECT_ROOT / "data" / "processed"


# ═══════════════════════════════════════════════════════════════
#  1. Data Generation Tests
# ═══════════════════════════════════════════════════════════════
class TestDataGeneration:
    """Verify that raw CSVs exist and have expected columns."""

    @pytest.fixture(autouse=True)
    def _check_raw_dir(self):
        if not RAW_DIR.exists() or not list(RAW_DIR.glob("*.csv")):
            pytest.skip("Raw data not generated — run scripts/generate_data.py first")

    @pytest.mark.parametrize("filename,min_rows", [
        ("customers.csv",  100),
        ("categories.csv",  5),
        ("products.csv",    50),
        ("stores.csv",       5),
        ("orders.csv",    1000),
        ("order_items.csv", 2000),
        ("inventory.csv",  100),
    ])
    def test_raw_csv_exists_and_has_rows(self, filename, min_rows):
        path = RAW_DIR / filename
        assert path.exists(), f"{filename} missing"
        df = pd.read_csv(path)
        assert len(df) >= min_rows, f"{filename}: expected >= {min_rows} rows, got {len(df)}"


# ═══════════════════════════════════════════════════════════════
#  2. Cleaning Tests
# ═══════════════════════════════════════════════════════════════
class TestCleaning:
    """Verify cleaning removes dirty data correctly."""

    @pytest.fixture(autouse=True)
    def _check_raw(self):
        if not RAW_DIR.exists():
            pytest.skip("Raw data not generated")

    def test_customers_deduplication(self):
        raw = pd.read_csv(RAW_DIR / "customers.csv")
        cleaned = clean_customers(raw)
        # Should have no duplicate emails.
        assert cleaned["email"].is_unique

    def test_products_price_capping(self):
        raw = pd.read_csv(RAW_DIR / "products.csv")
        cleaned = clean_products(raw)
        cap = raw["unit_price"].quantile(0.98)
        assert cleaned["unit_price"].max() <= cap + 0.01

    def test_orders_valid_status(self):
        raw = pd.read_csv(RAW_DIR / "orders.csv")
        cleaned = clean_orders(raw)
        assert set(cleaned["status"].unique()).issubset({"Completed", "Returned", "Cancelled"})

    def test_order_items_positive_quantity(self):
        raw = pd.read_csv(RAW_DIR / "order_items.csv")
        cleaned = clean_order_items(raw)
        assert (cleaned["quantity"] > 0).all()


# ═══════════════════════════════════════════════════════════════
#  3. Validation Tests
# ═══════════════════════════════════════════════════════════════
class TestValidation:
    """Run all validators on the cleaned data."""

    @pytest.fixture(autouse=True)
    def _check_processed(self):
        if not PROCESSED_DIR.exists() or not list(PROCESSED_DIR.glob("*.csv")):
            pytest.skip("Processed data not available — run scripts/clean_data.py first")

    def _load(self, name):
        return pd.read_csv(PROCESSED_DIR / f"{name}.csv")

    def test_all_validations_pass(self):
        results = run_all_validations(
            self._load("customers"),
            self._load("categories"),
            self._load("products"),
            self._load("stores"),
            self._load("orders"),
            self._load("order_items"),
            self._load("inventory"),
        )
        for table, issues in results.items():
            assert issues == [], f"{table}: {issues}"


# ═══════════════════════════════════════════════════════════════
#  4. Database Tests
# ═══════════════════════════════════════════════════════════════
class TestDatabase:
    """Verify data was loaded into MySQL correctly."""

    @pytest.fixture(autouse=True)
    def _check_db(self):
        try:
            engine = get_engine()
            with engine.connect() as conn:
                conn.execute(__import__("sqlalchemy").text("SELECT 1"))
        except Exception:
            pytest.skip("MySQL not available")

    @pytest.mark.parametrize("table,min_rows", [
        ("customers",   100),
        ("categories",    5),
        ("products",     50),
        ("stores",        5),
        ("orders",     1000),
        ("order_items", 2000),
        ("inventory",   100),
    ])
    def test_table_has_rows(self, table, min_rows):
        df = run_query(f"SELECT COUNT(*) AS cnt FROM {table}")
        assert df["cnt"].iloc[0] >= min_rows

    def test_revenue_kpi_query(self):
        df = run_query("""
            SELECT ROUND(SUM(oi.line_total), 2) AS total_revenue
            FROM orders o
            JOIN order_items oi ON o.order_id = oi.order_id
            WHERE o.status = 'Completed'
        """)
        assert df["total_revenue"].iloc[0] > 0

    def test_no_orphan_order_items(self):
        df = run_query("""
            SELECT COUNT(*) AS cnt
            FROM order_items oi
            LEFT JOIN orders o ON oi.order_id = o.order_id
            WHERE o.order_id IS NULL
        """)
        assert df["cnt"].iloc[0] == 0


# ═══════════════════════════════════════════════════════════════
#  5. Analytics Tests
# ═══════════════════════════════════════════════════════════════
class TestAnalytics:
    """Verify analytics functions return valid DataFrames."""

    @pytest.fixture(autouse=True)
    def _check_db(self):
        try:
            engine = get_engine()
            with engine.connect() as conn:
                conn.execute(__import__("sqlalchemy").text("SELECT 1"))
        except Exception:
            pytest.skip("MySQL not available")

    def test_get_revenue_kpis(self):
        from src.analytics import get_revenue_kpis
        kpis = get_revenue_kpis()
        assert "total_revenue" in kpis
        assert kpis["total_revenue"] > 0

    def test_get_monthly_revenue(self):
        from src.analytics import get_monthly_revenue
        df = get_monthly_revenue()
        assert not df.empty
        assert "month" in df.columns
        assert "revenue" in df.columns

    def test_get_top_products(self):
        from src.analytics import get_top_products
        df = get_top_products(5)
        assert len(df) == 5

    def test_get_low_stock_alerts(self):
        from src.analytics import get_low_stock_alerts
        df = get_low_stock_alerts()
        assert isinstance(df, pd.DataFrame)
        # Every row should have qty < reorder level.
        if not df.empty:
            assert (df["qty_on_hand"] < df["reorder_level"]).all()
