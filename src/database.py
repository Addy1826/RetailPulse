# database.py - Handles database connection and running queries
# Connects to MySQL locally; automatically falls back to SQLite for cloud deployment.

import os
import sqlite3
from pathlib import Path

import pandas as pd
from dotenv import load_dotenv
from sqlalchemy import create_engine, event, text

# Load .env from project root
PROJECT_ROOT = Path(__file__).resolve().parents[1]
load_dotenv(PROJECT_ROOT / ".env")

SQLITE_PATH = PROJECT_ROOT / "data" / "retailpulse.db"


def _sqlite_setup(conn, record):
    """Register MySQL-compatible helper functions in SQLite."""
    def date_format(val, fmt):
        if val is None:
            return ""
        return pd.to_datetime(val).strftime(fmt.replace("%%", "%"))

    def dayname(val):
        if val is None:
            return ""
        return pd.to_datetime(val).strftime("%A")

    def dayofweek(val):
        if val is None:
            return 1
        # MySQL DAYOFWEEK: 1=Sunday, 2=Monday, ..., 7=Saturday
        return ((pd.to_datetime(val).dayofweek + 1) % 7) + 1

    cursor = conn.cursor()
    cursor.execute("PRAGMA foreign_keys = ON;")
    cursor.close()

    conn.create_function("DATE_FORMAT", 2, date_format)
    conn.create_function("DAYNAME", 1, dayname)
    conn.create_function("DAYOFWEEK", 1, dayofweek)


def get_engine():
    """Create and return a SQLAlchemy engine for MySQL, or SQLite fallback."""
    if hasattr(get_engine, "_engine") and get_engine._engine is not None:
        return get_engine._engine

    user = os.getenv("DB_USER", "root")
    pwd = os.getenv("DB_PASSWORD", "")
    host = os.getenv("DB_HOST", "localhost")
    port = os.getenv("DB_PORT", "3306")
    db = os.getenv("DB_NAME", "retailpulse")

    mysql_url = f"mysql+pymysql://{user}:{pwd}@{host}:{port}/{db}"

    # Try MySQL first
    try:
        mysql_engine = create_engine(mysql_url, pool_pre_ping=True)
        with mysql_engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        get_engine._engine = mysql_engine
        return get_engine._engine
    except Exception:
        # Fall back to SQLite for Streamlit Cloud deployment
        if not SQLITE_PATH.exists():
            # Build database if not present
            from scripts.build_sqlite_db import DB_PATH  # noqa: F401
        sqlite_engine = create_engine(f"sqlite:///{SQLITE_PATH.as_posix()}")
        event.listen(sqlite_engine, "connect", _sqlite_setup)
        get_engine._engine = sqlite_engine
        return get_engine._engine


def run_query(sql, params=None):
    """Run a SELECT query and return results as a DataFrame."""
    engine = get_engine()
    with engine.connect() as conn:
        return pd.read_sql(text(sql), conn, params=params)


def run_execute(sql, params=None):
    """Run an INSERT/UPDATE/DELETE and return the number of affected rows."""
    engine = get_engine()
    with engine.begin() as conn:
        result = conn.execute(text(sql), params or {})
        return result.rowcount


def run_script(sql_path):
    """Run a .sql file with multiple statements."""
    sql_text = Path(sql_path).read_text(encoding="utf-8")
    engine = get_engine()
    with engine.begin() as conn:
        for stmt in sql_text.split(";"):
            stmt = stmt.strip()
            if stmt:
                conn.execute(text(stmt))


def load_dataframe(df, table, if_exists="append"):
    """Load a pandas DataFrame into the database table."""
    engine = get_engine()
    rows = df.to_sql(table, engine, if_exists=if_exists, index=False,
                     chunksize=500)
    return rows if rows else len(df)
