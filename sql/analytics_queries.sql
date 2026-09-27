-- RetailPulse - Analytics Queries
-- Simple queries to analyze sales, products, customers and inventory

USE retailpulse;


-- 1. Total sales summary
SELECT
    COUNT(DISTINCT o.order_id) AS total_orders,
    SUM(oi.quantity * oi.selling_price) AS total_revenue,
    AVG(oi.quantity * oi.selling_price) AS avg_order_value,
    COUNT(DISTINCT o.Customer_id) AS unique_customers
FROM orders o
INNER JOIN order_items oi ON o.order_id = oi.order_id
WHERE o.order_status = 'Completed';


-- 2. Monthly sales trend
SELECT
    DATE_FORMAT(o.Order_date, '%Y-%m') AS month,
    SUM(oi.quantity * oi.selling_price) AS revenue,
    COUNT(DISTINCT o.order_id) AS orders
FROM orders o
INNER JOIN order_items oi ON o.order_id = oi.order_id
WHERE o.order_status = 'Completed'
GROUP BY month
ORDER BY month;


-- 3. Top 10 best selling products
SELECT
    p.product_name,
    p.category,
    SUM(oi.quantity) AS units_sold,
    SUM(oi.quantity * oi.selling_price) AS revenue
FROM order_items oi
INNER JOIN products p ON oi.product_id = p.product_id
INNER JOIN orders o ON oi.order_id = o.order_id
WHERE o.order_status = 'Completed'
GROUP BY p.product_id, p.product_name, p.category
ORDER BY revenue DESC
LIMIT 10;


-- 4. Revenue by category
SELECT
    p.category,
    SUM(oi.quantity) AS units_sold,
    SUM(oi.quantity * oi.selling_price) AS revenue
FROM order_items oi
INNER JOIN products p ON oi.product_id = p.product_id
INNER JOIN orders o ON oi.order_id = o.order_id
WHERE o.order_status = 'Completed'
GROUP BY p.category
ORDER BY revenue DESC;


-- 5. Revenue by store
SELECT
    s.store_name,
    s.city,
    COUNT(DISTINCT o.order_id) AS orders,
    SUM(oi.quantity * oi.selling_price) AS revenue
FROM orders o
INNER JOIN stores s ON o.store_id = s.store_id
INNER JOIN order_items oi ON o.order_id = oi.order_id
WHERE o.order_status = 'Completed'
GROUP BY s.store_id, s.store_name, s.city
ORDER BY revenue DESC;


-- 6. Customer sales by city
SELECT
    c.city,
    COUNT(DISTINCT c.Customer_Id) AS total_customers,
    COUNT(DISTINCT o.order_id) AS orders,
    SUM(oi.quantity * oi.selling_price) AS revenue
FROM Customers c
INNER JOIN orders o ON c.Customer_Id = o.Customer_id
INNER JOIN order_items oi ON o.order_id = oi.order_id
WHERE o.order_status = 'Completed'
GROUP BY c.city
ORDER BY revenue DESC;


-- 7. Payment method distribution
SELECT
    o.payment_method,
    COUNT(DISTINCT o.order_id) AS order_count,
    SUM(oi.quantity * oi.selling_price) AS total_amount
FROM orders o
INNER JOIN order_items oi ON o.order_id = oi.order_id
WHERE o.order_status = 'Completed'
GROUP BY o.payment_method
ORDER BY total_amount DESC;


-- 8. Top 10 spending customers
SELECT
    c.Customer_Id,
    c.Customer_name,
    c.city,
    COUNT(DISTINCT o.order_id) AS total_orders,
    SUM(oi.quantity * oi.selling_price) AS total_spent
FROM Customers c
INNER JOIN orders o ON c.Customer_Id = o.Customer_id
INNER JOIN order_items oi ON o.order_id = oi.order_id
WHERE o.order_status = 'Completed'
GROUP BY c.Customer_Id, c.Customer_name, c.city
ORDER BY total_spent DESC
LIMIT 10;


-- 9. Low stock inventory alerts
SELECT
    s.store_name,
    p.product_name,
    p.category,
    inv.stock_quantity,
    p.recorder_level,
    inv.last_updated
FROM inventory inv
INNER JOIN stores s ON inv.store_id = s.store_id
INNER JOIN products p ON inv.product_id = p.product_id
WHERE inv.stock_quantity < p.recorder_level
ORDER BY inv.stock_quantity ASC;


-- 10. Store performance leaderboard
SELECT
    s.store_name,
    s.city,
    COUNT(DISTINCT o.order_id) AS total_orders,
    SUM(oi.quantity * oi.selling_price) AS revenue,
    COUNT(DISTINCT o.Customer_id) AS unique_customers
FROM stores s
INNER JOIN orders o ON s.store_id = o.store_id
INNER JOIN order_items oi ON o.order_id = oi.order_id
WHERE o.order_status = 'Completed'
GROUP BY s.store_id, s.store_name, s.city
ORDER BY revenue DESC;


-- 11. Most profitable products
SELECT
    p.product_name,
    p.category,
    SUM(oi.quantity) AS units_sold,
    SUM(oi.quantity * oi.selling_price) AS total_revenue,
    SUM(oi.quantity * p.Unit_price) AS total_cost,
    SUM(oi.quantity * oi.selling_price) - SUM(oi.quantity * p.Unit_price) AS profit
FROM order_items oi
INNER JOIN products p ON oi.product_id = p.product_id
INNER JOIN orders o ON oi.order_id = o.order_id
WHERE o.order_status = 'Completed'
GROUP BY p.product_id, p.product_name, p.category
ORDER BY profit DESC
LIMIT 10;


-- 12. Day of week shopping patterns
SELECT
    DAYNAME(o.Order_date) AS day_name,
    DAYOFWEEK(o.Order_date) AS day_num,
    COUNT(DISTINCT o.order_id) AS orders,
    SUM(oi.quantity * oi.selling_price) AS revenue
FROM orders o
INNER JOIN order_items oi ON o.order_id = oi.order_id
WHERE o.order_status = 'Completed'
GROUP BY day_name, day_num
ORDER BY day_num;
