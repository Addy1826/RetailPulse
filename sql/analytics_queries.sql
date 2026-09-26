-- RetailPulse - Analytics Queries
-- Simple queries to analyze sales, products, customers and inventory.

USE retailpulse;


-- Q1: Overall sales summary
SELECT
    COUNT(DISTINCT o.order_id)    AS total_orders,
    SUM(oi.line_total)            AS total_revenue,
    AVG(o.total_amount)           AS avg_order_value,
    COUNT(DISTINCT o.customer_id) AS unique_customers
FROM orders o
INNER JOIN order_items oi ON o.order_id = oi.order_id
WHERE o.status = 'Completed';


-- Q2: Monthly revenue
SELECT
    DATE_FORMAT(o.order_date, '%Y-%m') AS month,
    SUM(oi.line_total)                 AS revenue,
    COUNT(DISTINCT o.order_id)         AS orders
FROM orders o
INNER JOIN order_items oi ON o.order_id = oi.order_id
WHERE o.status = 'Completed'
GROUP BY month
ORDER BY month;


-- Q3: Top 10 best selling products
SELECT
    p.product_name,
    p.brand,
    c.category_name,
    SUM(oi.quantity)    AS units_sold,
    SUM(oi.line_total)  AS revenue
FROM order_items oi
INNER JOIN products p   ON oi.product_id = p.product_id
INNER JOIN categories c ON p.category_id = c.category_id
INNER JOIN orders o     ON oi.order_id = o.order_id
WHERE o.status = 'Completed'
GROUP BY p.product_id, p.product_name, p.brand, c.category_name
ORDER BY revenue DESC
LIMIT 10;


-- Q4: Revenue by category
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
ORDER BY revenue DESC;


-- Q5: Revenue by store region
SELECT
    s.region,
    COUNT(DISTINCT o.order_id) AS orders,
    SUM(oi.line_total)         AS revenue
FROM orders o
INNER JOIN stores s      ON o.store_id = s.store_id
INNER JOIN order_items oi ON o.order_id = oi.order_id
WHERE o.status = 'Completed'
GROUP BY s.region
ORDER BY revenue DESC;


-- Q6: Customer segments - how much each segment spends
SELECT
    cu.segment,
    COUNT(DISTINCT cu.customer_id) AS customers,
    COUNT(DISTINCT o.order_id)     AS orders,
    SUM(oi.line_total)             AS revenue,
    SUM(oi.line_total) / COUNT(DISTINCT cu.customer_id) AS revenue_per_customer
FROM customers cu
INNER JOIN orders o      ON cu.customer_id = o.customer_id
INNER JOIN order_items oi ON o.order_id = oi.order_id
WHERE o.status = 'Completed'
GROUP BY cu.segment
ORDER BY revenue DESC;


-- Q7: Payment method breakdown
SELECT
    o.payment_method,
    COUNT(*)           AS order_count,
    SUM(o.total_amount) AS total_amount
FROM orders o
WHERE o.status = 'Completed'
GROUP BY o.payment_method
ORDER BY total_amount DESC;


-- Q8: Top 10 customers by total spending
SELECT
    cu.customer_id,
    CONCAT(cu.first_name, ' ', cu.last_name) AS customer_name,
    cu.segment,
    cu.city,
    COUNT(DISTINCT o.order_id) AS total_orders,
    SUM(oi.line_total)         AS lifetime_value
FROM customers cu
INNER JOIN orders o      ON cu.customer_id = o.customer_id
INNER JOIN order_items oi ON o.order_id = oi.order_id
WHERE o.status = 'Completed'
GROUP BY cu.customer_id, customer_name, cu.segment, cu.city
ORDER BY lifetime_value DESC
LIMIT 10;


-- Q9: Products that are running low on stock
SELECT
    s.store_name,
    p.product_name,
    p.sku,
    inv.qty_on_hand,
    inv.reorder_level,
    inv.last_restock
FROM inventory inv
INNER JOIN stores s   ON inv.store_id = s.store_id
INNER JOIN products p ON inv.product_id = p.product_id
WHERE inv.qty_on_hand < inv.reorder_level
ORDER BY inv.qty_on_hand ASC;


-- Q10: Store performance - which stores make the most money
SELECT
    s.store_name,
    s.city,
    s.region,
    s.store_type,
    COUNT(DISTINCT o.order_id)    AS total_orders,
    SUM(oi.line_total)            AS revenue,
    COUNT(DISTINCT o.customer_id) AS unique_customers
FROM stores s
INNER JOIN orders o      ON s.store_id = o.store_id
INNER JOIN order_items oi ON o.order_id = oi.order_id
WHERE o.status = 'Completed'
GROUP BY s.store_id, s.store_name, s.city, s.region, s.store_type
ORDER BY revenue DESC;


-- Q11: Most profitable products (revenue minus cost)
SELECT
    p.product_name,
    p.brand,
    c.category_name,
    SUM(oi.quantity)                                       AS units_sold,
    SUM(oi.line_total)                                     AS revenue,
    SUM(oi.quantity * p.cost_price)                         AS total_cost,
    SUM(oi.line_total) - SUM(oi.quantity * p.cost_price)   AS gross_profit
FROM order_items oi
INNER JOIN products p   ON oi.product_id = p.product_id
INNER JOIN categories c ON p.category_id = c.category_id
INNER JOIN orders o     ON oi.order_id = o.order_id
WHERE o.status = 'Completed'
GROUP BY p.product_id, p.product_name, p.brand, c.category_name
HAVING SUM(oi.line_total) > 0
ORDER BY gross_profit DESC
LIMIT 10;


-- Q12: Orders by day of the week
SELECT
    DAYNAME(o.order_date)          AS day_name,
    DAYOFWEEK(o.order_date)        AS day_num,
    COUNT(DISTINCT o.order_id)     AS orders,
    SUM(oi.line_total)             AS revenue
FROM orders o
INNER JOIN order_items oi ON o.order_id = oi.order_id
WHERE o.status = 'Completed'
GROUP BY day_name, day_num
ORDER BY day_num;
