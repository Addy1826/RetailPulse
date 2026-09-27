-- RetailPulse - SQL Analytics Queries
-- Business-driven analytics queries for retail sales and inventory performance

USE retailpulse;


-- 1. Executive Sales KPI Summary
SELECT
    COUNT(DISTINCT o.order_id)                                                  AS total_orders,
    SUM(oi.quantity * oi.selling_price)                                         AS total_revenue,
    SUM(oi.quantity * oi.selling_price) / NULLIF(COUNT(DISTINCT o.order_id), 0) AS avg_order_value,
    COUNT(DISTINCT o.Customer_id)                                               AS unique_customers
FROM orders o
INNER JOIN order_items oi ON o.order_id = oi.order_id
WHERE o.order_status = 'Completed';


-- 2. Monthly Revenue and Order Trend
SELECT
    DATE_FORMAT(o.Order_date, '%Y-%m')  AS month,
    SUM(oi.quantity * oi.selling_price) AS revenue,
    COUNT(DISTINCT o.order_id)          AS orders
FROM orders o
INNER JOIN order_items oi ON o.order_id = oi.order_id
WHERE o.order_status = 'Completed'
GROUP BY month
ORDER BY month;


-- 3. Top 10 Products by Revenue
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
LIMIT 10;


-- 4. Category Sales Performance
SELECT
    p.category,
    SUM(oi.quantity)                    AS units_sold,
    SUM(oi.quantity * oi.selling_price) AS revenue
FROM order_items oi
INNER JOIN products p ON oi.product_id = p.product_id
INNER JOIN orders o ON oi.order_id = o.order_id
WHERE o.order_status = 'Completed'
GROUP BY p.category
ORDER BY revenue DESC;


-- 5. Store Revenue Performance
SELECT
    s.store_name,
    s.city,
    COUNT(DISTINCT o.order_id)          AS orders,
    SUM(oi.quantity * oi.selling_price) AS revenue
FROM orders o
INNER JOIN stores s ON o.store_id = s.store_id
INNER JOIN order_items oi ON o.order_id = oi.order_id
WHERE o.order_status = 'Completed'
GROUP BY s.store_id, s.store_name, s.city
ORDER BY revenue DESC;


-- 6. Customer Revenue by City
SELECT
    c.city,
    COUNT(DISTINCT c.Customer_Id)       AS total_customers,
    COUNT(DISTINCT o.order_id)          AS orders,
    SUM(oi.quantity * oi.selling_price) AS revenue
FROM Customers c
INNER JOIN orders o ON c.Customer_Id = o.Customer_id
INNER JOIN order_items oi ON o.order_id = oi.order_id
WHERE o.order_status = 'Completed'
GROUP BY c.city
ORDER BY revenue DESC;


-- 7. Payment Method Performance
SELECT
    o.payment_method,
    COUNT(DISTINCT o.order_id)          AS order_count,
    SUM(oi.quantity * oi.selling_price) AS total_amount
FROM orders o
INNER JOIN order_items oi ON o.order_id = oi.order_id
WHERE o.order_status = 'Completed'
GROUP BY o.payment_method
ORDER BY total_amount DESC;


-- 8. Top 10 Customers by Completed-Order Spend
SELECT
    c.Customer_Id,
    c.Customer_name,
    c.city,
    COUNT(DISTINCT o.order_id)          AS total_orders,
    SUM(oi.quantity * oi.selling_price) AS total_spent
FROM Customers c
INNER JOIN orders o ON c.Customer_Id = o.Customer_id
INNER JOIN order_items oi ON o.order_id = oi.order_id
WHERE o.order_status = 'Completed'
GROUP BY c.Customer_Id, c.Customer_name, c.city
ORDER BY total_spent DESC
LIMIT 10;


-- 9. Low-Stock Inventory Alerts
SELECT
    s.store_name,
    p.product_name,
    p.category,
    inv.stock_quantity,
    p.reorder_level,
    inv.last_updated
FROM inventory inv
INNER JOIN stores s ON inv.store_id = s.store_id
INNER JOIN products p ON inv.product_id = p.product_id
WHERE inv.stock_quantity < p.reorder_level
ORDER BY inv.stock_quantity ASC;


-- 10. Store Performance Leaderboard
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
ORDER BY revenue DESC;


-- 11. Product Gross-Margin Analysis
SELECT
    p.product_name,
    p.category,
    SUM(oi.quantity)                                                      AS units_sold,
    SUM(oi.quantity * oi.selling_price)                                   AS total_revenue,
    SUM(oi.quantity * p.Unit_price)                                       AS estimated_cost,
    SUM(oi.quantity * oi.selling_price) - SUM(oi.quantity * p.Unit_price) AS estimated_gross_margin
FROM order_items oi
INNER JOIN products p ON oi.product_id = p.product_id
INNER JOIN orders o ON oi.order_id = o.order_id
WHERE o.order_status = 'Completed'
GROUP BY p.product_id, p.product_name, p.category
ORDER BY estimated_gross_margin DESC
LIMIT 10;


-- 12. Day-of-Week Sales Pattern
SELECT
    DAYNAME(o.Order_date)               AS day_name,
    DAYOFWEEK(o.Order_date)             AS day_num,
    COUNT(DISTINCT o.order_id)          AS orders,
    SUM(oi.quantity * oi.selling_price) AS revenue
FROM orders o
INNER JOIN order_items oi ON o.order_id = oi.order_id
WHERE o.order_status = 'Completed'
GROUP BY day_name, day_num
ORDER BY day_num;


-- 13. Repeat / High-Frequency Customers (HAVING demonstration)
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
HAVING COUNT(DISTINCT o.order_id) >= 6
ORDER BY completed_orders DESC, total_spent DESC;


-- 14. Customers With No Orders (LEFT JOIN Anti-Join demonstration)
SELECT
    c.Customer_Id,
    c.Customer_name,
    c.city
FROM Customers c
LEFT JOIN orders o ON c.Customer_Id = o.Customer_id
WHERE o.order_id IS NULL
ORDER BY c.Customer_Id;
