# analytics.py - Functions that query MySQL and return DataFrames for the dashboard

import pandas as pd
from src.database import run_query


# --- KPI functions ---

def get_revenue_kpis():
    """Get the main sales numbers."""
    df = run_query("""
        SELECT
            COUNT(DISTINCT o.order_id)    AS total_orders,
            SUM(oi.line_total)            AS total_revenue,
            AVG(o.total_amount)           AS avg_order_value,
            COUNT(DISTINCT o.customer_id) AS unique_customers
        FROM orders o
        INNER JOIN order_items oi ON o.order_id = oi.order_id
        WHERE o.status = 'Completed'
    """)
    return df.iloc[0].to_dict()


def get_total_products():
    df = run_query("SELECT COUNT(*) AS cnt FROM products WHERE is_active = 1")
    return int(df["cnt"].iloc[0])


def get_total_stores():
    df = run_query("SELECT COUNT(*) AS cnt FROM stores")
    return int(df["cnt"].iloc[0])


# --- Trends ---

def get_monthly_revenue():
    return run_query("""
        SELECT
            DATE_FORMAT(o.order_date, '%%Y-%%m') AS month,
            SUM(oi.line_total)                   AS revenue,
            COUNT(DISTINCT o.order_id)           AS orders
        FROM orders o
        INNER JOIN order_items oi ON o.order_id = oi.order_id
        WHERE o.status = 'Completed'
        GROUP BY month
        ORDER BY month
    """)


def get_daily_patterns():
    return run_query("""
        SELECT
            DAYNAME(o.order_date)      AS day_name,
            DAYOFWEEK(o.order_date)    AS day_num,
            COUNT(DISTINCT o.order_id) AS orders,
            SUM(oi.line_total)         AS revenue
        FROM orders o
        INNER JOIN order_items oi ON o.order_id = oi.order_id
        WHERE o.status = 'Completed'
        GROUP BY day_name, day_num
        ORDER BY day_num
    """)


# --- Product analytics ---

def get_top_products(limit=10):
    return run_query(f"""
        SELECT
            p.product_name, p.brand, c.category_name,
            SUM(oi.quantity)   AS units_sold,
            SUM(oi.line_total) AS revenue
        FROM order_items oi
        INNER JOIN products p   ON oi.product_id = p.product_id
        INNER JOIN categories c ON p.category_id = c.category_id
        INNER JOIN orders o     ON oi.order_id = o.order_id
        WHERE o.status = 'Completed'
        GROUP BY p.product_id, p.product_name, p.brand, c.category_name
        ORDER BY revenue DESC
        LIMIT {int(limit)}
    """)


def get_category_revenue():
    return run_query("""
        SELECT
            c.category_name,
            SUM(oi.quantity)   AS units_sold,
            SUM(oi.line_total) AS revenue
        FROM order_items oi
        INNER JOIN products p   ON oi.product_id = p.product_id
        INNER JOIN categories c ON p.category_id = c.category_id
        INNER JOIN orders o     ON oi.order_id = o.order_id
        WHERE o.status = 'Completed'
        GROUP BY c.category_name
        ORDER BY revenue DESC
    """)


def get_profit_margins(limit=10):
    return run_query(f"""
        SELECT
            p.product_name, p.brand, c.category_name,
            SUM(oi.quantity)                                     AS units_sold,
            SUM(oi.line_total)                                   AS revenue,
            SUM(oi.quantity * p.cost_price)                       AS total_cost,
            SUM(oi.line_total) - SUM(oi.quantity * p.cost_price) AS gross_profit,
            (SUM(oi.line_total) - SUM(oi.quantity * p.cost_price))
                / SUM(oi.line_total) * 100                       AS margin_pct
        FROM order_items oi
        INNER JOIN products p   ON oi.product_id = p.product_id
        INNER JOIN categories c ON p.category_id = c.category_id
        INNER JOIN orders o     ON oi.order_id = o.order_id
        WHERE o.status = 'Completed'
        GROUP BY p.product_id, p.product_name, p.brand, c.category_name
        HAVING SUM(oi.line_total) > 0
        ORDER BY gross_profit DESC
        LIMIT {int(limit)}
    """)


# --- Store analytics ---

def get_region_revenue():
    return run_query("""
        SELECT
            s.region,
            COUNT(DISTINCT o.order_id) AS orders,
            SUM(oi.line_total)         AS revenue
        FROM orders o
        INNER JOIN stores s       ON o.store_id = s.store_id
        INNER JOIN order_items oi ON o.order_id = oi.order_id
        WHERE o.status = 'Completed'
        GROUP BY s.region
        ORDER BY revenue DESC
    """)


def get_store_performance():
    return run_query("""
        SELECT
            s.store_name, s.city, s.region, s.store_type,
            COUNT(DISTINCT o.order_id)    AS total_orders,
            SUM(oi.line_total)            AS revenue,
            COUNT(DISTINCT o.customer_id) AS unique_customers
        FROM stores s
        INNER JOIN orders o       ON s.store_id = o.store_id
        INNER JOIN order_items oi ON o.order_id = oi.order_id
        WHERE o.status = 'Completed'
        GROUP BY s.store_id, s.store_name, s.city, s.region, s.store_type
        ORDER BY revenue DESC
    """)


# --- Customer analytics ---

def get_customer_segments():
    return run_query("""
        SELECT
            cu.segment,
            COUNT(DISTINCT cu.customer_id) AS customers,
            COUNT(DISTINCT o.order_id)     AS orders,
            SUM(oi.line_total)             AS revenue,
            SUM(oi.line_total) / COUNT(DISTINCT cu.customer_id) AS revenue_per_customer
        FROM customers cu
        INNER JOIN orders o       ON cu.customer_id = o.customer_id
        INNER JOIN order_items oi ON o.order_id = oi.order_id
        WHERE o.status = 'Completed'
        GROUP BY cu.segment
        ORDER BY revenue DESC
    """)


def get_top_customers(limit=10):
    return run_query(f"""
        SELECT
            cu.customer_id,
            CONCAT(cu.first_name, ' ', cu.last_name) AS customer_name,
            cu.segment, cu.city,
            COUNT(DISTINCT o.order_id) AS total_orders,
            SUM(oi.line_total)         AS lifetime_value
        FROM customers cu
        INNER JOIN orders o       ON cu.customer_id = o.customer_id
        INNER JOIN order_items oi ON o.order_id = oi.order_id
        WHERE o.status = 'Completed'
        GROUP BY cu.customer_id, customer_name, cu.segment, cu.city
        ORDER BY lifetime_value DESC
        LIMIT {int(limit)}
    """)


def get_payment_methods():
    return run_query("""
        SELECT
            o.payment_method,
            COUNT(*)            AS order_count,
            SUM(o.total_amount) AS total_amount
        FROM orders o
        WHERE o.status = 'Completed'
        GROUP BY o.payment_method
        ORDER BY total_amount DESC
    """)


# --- Inventory ---

def get_low_stock_alerts():
    return run_query("""
        SELECT
            s.store_name,
            p.product_name, p.sku,
            inv.qty_on_hand, inv.reorder_level, inv.last_restock
        FROM inventory inv
        INNER JOIN stores s   ON inv.store_id = s.store_id
        INNER JOIN products p ON inv.product_id = p.product_id
        WHERE inv.qty_on_hand < inv.reorder_level
        ORDER BY inv.qty_on_hand ASC
    """)


def get_inventory_summary():
    return run_query("""
        SELECT
            c.category_name,
            SUM(inv.qty_on_hand) AS total_stock,
            AVG(inv.qty_on_hand) AS avg_stock,
            SUM(CASE WHEN inv.qty_on_hand < inv.reorder_level THEN 1 ELSE 0 END) AS low_stock_count
        FROM inventory inv
        INNER JOIN products p   ON inv.product_id = p.product_id
        INNER JOIN categories c ON p.category_id = c.category_id
        GROUP BY c.category_name
        ORDER BY total_stock DESC
    """)
