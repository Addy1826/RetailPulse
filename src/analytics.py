# analytics.py - Functions that query the database and return DataFrames for the dashboard

import pandas as pd
from src.database import run_query


# --- Summary KPIs ---

def get_revenue_kpis():
    """Get overall sales KPIs with true Average Order Value (total revenue / completed orders)."""
    df = run_query("""
        SELECT
            COUNT(DISTINCT o.order_id)                                                  AS total_orders,
            SUM(oi.quantity * oi.selling_price)                                         AS total_revenue,
            SUM(oi.quantity * oi.selling_price) / NULLIF(COUNT(DISTINCT o.order_id), 0) AS avg_order_value,
            COUNT(DISTINCT o.Customer_id)                                               AS unique_customers
        FROM orders o
        INNER JOIN order_items oi ON o.order_id = oi.order_id
        WHERE o.order_status = 'Completed'
    """)
    return df.iloc[0].to_dict()


def get_total_products():
    """Count of total products in catalog."""
    df = run_query("SELECT COUNT(*) AS cnt FROM products")
    return int(df["cnt"].iloc[0])


def get_total_stores():
    """Count of total retail stores."""
    df = run_query("SELECT COUNT(*) AS cnt FROM stores")
    return int(df["cnt"].iloc[0])


# --- Trends ---

def get_monthly_revenue():
    """Monthly revenue and order volume trend."""
    return run_query("""
        SELECT
            DATE_FORMAT(o.Order_date, '%Y-%m')  AS month,
            SUM(oi.quantity * oi.selling_price) AS revenue,
            COUNT(DISTINCT o.order_id)          AS orders
        FROM orders o
        INNER JOIN order_items oi ON o.order_id = oi.order_id
        WHERE o.order_status = 'Completed'
        GROUP BY month
        ORDER BY month
    """)


def get_daily_patterns():
    """Sales by day of the week."""
    return run_query("""
        SELECT
            DAYNAME(o.Order_date)               AS day_name,
            DAYOFWEEK(o.Order_date)             AS day_num,
            COUNT(DISTINCT o.order_id)          AS orders,
            SUM(oi.quantity * oi.selling_price) AS revenue
        FROM orders o
        INNER JOIN order_items oi ON o.order_id = oi.order_id
        WHERE o.order_status = 'Completed'
        GROUP BY day_name, day_num
        ORDER BY day_num
    """)


# --- Product analytics ---

def get_top_products(limit=10):
    """Top products by revenue."""
    return run_query(f"""
        SELECT
            p.product_name,
            p.category,
            SUM(oi.quantity)                    AS units_sold,
            SUM(oi.quantity * oi.selling_price) AS revenue
        FROM order_items oi
        INNER JOIN products p ON oi.product_id = p.product_id
        INNER JOIN orders o ON oi.order_id = o.order_id
        WHERE o.order_status = 'Completed'
        GROUP BY p.product_id, p.product_name, p.category
        ORDER BY revenue DESC
        LIMIT {int(limit)}
    """)


def get_category_revenue():
    """Revenue breakdown by product category."""
    return run_query("""
        SELECT
            p.category,
            p.category                          AS category_name,
            SUM(oi.quantity)                    AS units_sold,
            SUM(oi.quantity * oi.selling_price) AS revenue
        FROM order_items oi
        INNER JOIN products p ON oi.product_id = p.product_id
        INNER JOIN orders o ON oi.order_id = o.order_id
        WHERE o.order_status = 'Completed'
        GROUP BY p.category
        ORDER BY revenue DESC
    """)


def get_profit_margins(limit=10):
    """Estimated gross margin analysis comparing selling price to baseline unit price."""
    return run_query(f"""
        SELECT
            p.product_name,
            p.category,
            SUM(oi.quantity)                    AS units_sold,
            SUM(oi.quantity * oi.selling_price) AS total_revenue,
            SUM(oi.quantity * p.Unit_price)     AS estimated_cost,
            SUM(oi.quantity * oi.selling_price) - SUM(oi.quantity * p.Unit_price) AS estimated_gross_margin,
            SUM(oi.quantity * oi.selling_price) - SUM(oi.quantity * p.Unit_price) AS profit,
            ((SUM(oi.quantity * oi.selling_price) - SUM(oi.quantity * p.Unit_price)) / SUM(oi.quantity * oi.selling_price)) * 100 AS margin_pct
        FROM order_items oi
        INNER JOIN products p ON oi.product_id = p.product_id
        INNER JOIN orders o ON oi.order_id = o.order_id
        WHERE o.order_status = 'Completed'
        GROUP BY p.product_id, p.product_name, p.category
        ORDER BY estimated_gross_margin DESC
        LIMIT {int(limit)}
    """)


def get_gross_margins(limit=10):
    """Alias for estimated gross margin analysis."""
    return get_profit_margins(limit=limit)


# --- Store analytics ---

def get_store_performance():
    """Store leaderboard by revenue."""
    return run_query("""
        SELECT
            s.store_name,
            s.city,
            COUNT(DISTINCT o.order_id)          AS total_orders,
            SUM(oi.quantity * oi.selling_price) AS revenue,
            COUNT(DISTINCT o.Customer_id)       AS unique_customers
        FROM stores s
        INNER JOIN orders o ON s.store_id = o.store_id
        INNER JOIN order_items oi ON o.order_id = oi.order_id
        WHERE o.order_status = 'Completed'
        GROUP BY s.store_id, s.store_name, s.city
        ORDER BY revenue DESC
    """)


def get_region_revenue():
    """Sales by store city/region."""
    return run_query("""
        SELECT
            s.city AS region,
            COUNT(DISTINCT o.order_id)          AS orders,
            SUM(oi.quantity * oi.selling_price) AS revenue
        FROM orders o
        INNER JOIN stores s ON o.store_id = s.store_id
        INNER JOIN order_items oi ON o.order_id = oi.order_id
        WHERE o.order_status = 'Completed'
        GROUP BY s.city
        ORDER BY revenue DESC
    """)


# --- Customer analytics ---

def get_customer_segments():
    """Customer spending by city."""
    return run_query("""
        SELECT
            c.city AS segment,
            COUNT(DISTINCT c.Customer_Id)       AS customers,
            COUNT(DISTINCT o.order_id)          AS orders,
            SUM(oi.quantity * oi.selling_price) AS revenue,
            SUM(oi.quantity * oi.selling_price) / COUNT(DISTINCT c.Customer_Id) AS revenue_per_customer
        FROM Customers c
        INNER JOIN orders o ON c.Customer_Id = o.Customer_id
        INNER JOIN order_items oi ON o.order_id = oi.order_id
        WHERE o.order_status = 'Completed'
        GROUP BY c.city
        ORDER BY revenue DESC
    """)


def get_payment_methods():
    """Distribution of payment methods."""
    return run_query("""
        SELECT
            o.payment_method,
            COUNT(DISTINCT o.order_id)          AS order_count,
            SUM(oi.quantity * oi.selling_price) AS total_amount
        FROM orders o
        INNER JOIN order_items oi ON o.order_id = oi.order_id
        WHERE o.order_status = 'Completed'
        GROUP BY o.payment_method
        ORDER BY total_amount DESC
    """)


def get_top_customers(limit=10):
    """Top customers by spending."""
    return run_query(f"""
        SELECT
            c.Customer_Id,
            c.Customer_name,
            c.city,
            COUNT(DISTINCT o.order_id)          AS total_orders,
            SUM(oi.quantity * oi.selling_price) AS lifetime_value
        FROM Customers c
        INNER JOIN orders o ON c.Customer_Id = o.Customer_id
        INNER JOIN order_items oi ON o.order_id = oi.order_id
        WHERE o.order_status = 'Completed'
        GROUP BY c.Customer_Id, c.Customer_name, c.city
        ORDER BY lifetime_value DESC
        LIMIT {int(limit)}
    """)


def get_repeat_customers(min_orders=6):
    """Repeat/high-frequency customers with completed orders meeting minimum threshold."""
    return run_query(f"""
        SELECT
            c.Customer_Id,
            c.Customer_name,
            c.city,
            COUNT(DISTINCT o.order_id)          AS completed_orders,
            SUM(oi.quantity * oi.selling_price) AS total_spent
        FROM Customers c
        INNER JOIN orders o ON c.Customer_Id = o.Customer_id
        INNER JOIN order_items oi ON o.order_id = oi.order_id
        WHERE o.order_status = 'Completed'
        GROUP BY c.Customer_Id, c.Customer_name, c.city
        HAVING COUNT(DISTINCT o.order_id) >= {int(min_orders)}
        ORDER BY completed_orders DESC, total_spent DESC
    """)


def get_customers_with_no_orders():
    """Customers with zero orders via LEFT JOIN anti-join."""
    return run_query("""
        SELECT
            c.Customer_Id,
            c.Customer_name,
            c.city
        FROM Customers c
        LEFT JOIN orders o ON c.Customer_Id = o.Customer_id
        WHERE o.order_id IS NULL
        ORDER BY c.Customer_Id
    """)


# --- Inventory analytics ---

def get_low_stock_alerts():
    """Products where current stock is below reorder level."""
    return run_query("""
        SELECT
            s.store_name,
            p.product_name,
            p.category,
            inv.stock_quantity AS qty_on_hand,
            p.reorder_level,
            inv.last_updated
        FROM inventory inv
        INNER JOIN stores s ON inv.store_id = s.store_id
        INNER JOIN products p ON inv.product_id = p.product_id
        WHERE inv.stock_quantity < p.reorder_level
        ORDER BY inv.stock_quantity ASC
    """)


def get_inventory_summary():
    """Total stock and low stock counts by category."""
    return run_query("""
        SELECT
            p.category AS category_name,
            SUM(inv.stock_quantity) AS total_stock,
            SUM(CASE WHEN inv.stock_quantity < p.reorder_level THEN 1 ELSE 0 END) AS low_stock_count
        FROM inventory inv
        INNER JOIN products p ON inv.product_id = p.product_id
        GROUP BY p.category
        ORDER BY total_stock DESC
    """)
