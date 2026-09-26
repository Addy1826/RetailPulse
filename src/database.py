# database.py - Handles MySQL connection and running queries

import os
from pathlib import Path

import pandas as pd
from dotenv import load_dotenv
from sqlalchemy import create_engine, text

# Load .env from project root
env_path = Path(__file__).resolve().parents[1] / ".env"
load_dotenv(env_path)


def get_engine():
    """Create and return a SQLAlchemy engine for MySQL."""
    user = os.getenv("DB_USER", "root")
    pwd = os.getenv("DB_PASSWORD", "")
    host = os.getenv("DB_HOST", "localhost")
    port = os.getenv("DB_PORT", "3306")
    db = os.getenv("DB_NAME", "retailpulse")

    url = f"mysql+pymysql://{user}:{pwd}@{host}:{port}/{db}"

    if not hasattr(get_engine, "_engine"):
        get_engine._engine = create_engine(url, pool_pre_ping=True)
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
    """Load a pandas DataFrame into a MySQL table."""
    engine = get_engine()
    rows = df.to_sql(table, engine, if_exists=if_exists, index=False,
                     method="multi", chunksize=500)
    return rows if rows else len(df)
