-- RetailPulse Database Schema
-- 7 Normalized Tables for Retail Sales & Inventory Management

CREATE DATABASE IF NOT EXISTS retailpulse;
USE retailpulse;

-- 1. Categories
DROP TABLE IF EXISTS order_items;
DROP TABLE IF EXISTS inventory;
DROP TABLE IF EXISTS orders;
DROP TABLE IF EXISTS products;
DROP TABLE IF EXISTS stores;
DROP TABLE IF EXISTS customers;
DROP TABLE IF EXISTS categories;

CREATE TABLE categories (
    category_id     INT AUTO_INCREMENT PRIMARY KEY,
    category_name   VARCHAR(60) NOT NULL UNIQUE,
    description     VARCHAR(255)
);

-- 2. Customers
CREATE TABLE customers (
    customer_id     INT AUTO_INCREMENT PRIMARY KEY,
    first_name      VARCHAR(50) NOT NULL,
    last_name       VARCHAR(50) NOT NULL,
    email           VARCHAR(120) NOT NULL UNIQUE,
    phone           VARCHAR(20),
    city            VARCHAR(60),
    state           VARCHAR(40),
    join_date       DATE NOT NULL,
    segment         ENUM('Regular', 'Premium', 'VIP') DEFAULT 'Regular'
);

-- 3. Products
CREATE TABLE products (
    product_id      INT AUTO_INCREMENT PRIMARY KEY,
    product_name    VARCHAR(120) NOT NULL,
    category_id     INT NOT NULL,
    brand           VARCHAR(60),
    unit_price      DECIMAL(10,2) NOT NULL,
    cost_price      DECIMAL(10,2) NOT NULL,
    sku             VARCHAR(30) NOT NULL UNIQUE,
    is_active       TINYINT(1) DEFAULT 1,
    FOREIGN KEY (category_id) REFERENCES categories(category_id)
);

-- 4. Stores
CREATE TABLE stores (
    store_id        INT AUTO_INCREMENT PRIMARY KEY,
    store_name      VARCHAR(80) NOT NULL,
    city            VARCHAR(60) NOT NULL,
    state           VARCHAR(40) NOT NULL,
    region          ENUM('North', 'South', 'East', 'West') NOT NULL,
    store_type      ENUM('Flagship', 'Mall', 'Outlet', 'Online') NOT NULL,
    open_date       DATE NOT NULL
);

-- 5. Orders
CREATE TABLE orders (
    order_id        INT AUTO_INCREMENT PRIMARY KEY,
    customer_id     INT NOT NULL,
    store_id        INT NOT NULL,
    order_date      DATETIME NOT NULL,
    status          ENUM('Completed', 'Returned', 'Cancelled') DEFAULT 'Completed',
    payment_method  ENUM('Credit Card', 'Debit Card', 'UPI', 'Cash', 'Wallet') NOT NULL,
    total_amount    DECIMAL(12,2) NOT NULL DEFAULT 0.00,
    FOREIGN KEY (customer_id) REFERENCES customers(customer_id),
    FOREIGN KEY (store_id) REFERENCES stores(store_id)
);

-- 6. Order Items
CREATE TABLE order_items (
    item_id         INT AUTO_INCREMENT PRIMARY KEY,
    order_id        INT NOT NULL,
    product_id      INT NOT NULL,
    quantity        INT NOT NULL CHECK (quantity > 0),
    unit_price      DECIMAL(10,2) NOT NULL,
    discount_pct    DECIMAL(5,2) DEFAULT 0.00,
    line_total      DECIMAL(12,2) GENERATED ALWAYS AS (quantity * unit_price * (1 - discount_pct / 100)) STORED,
    FOREIGN KEY (order_id) REFERENCES orders(order_id),
    FOREIGN KEY (product_id) REFERENCES products(product_id)
);

-- 7. Inventory
CREATE TABLE inventory (
    inventory_id    INT AUTO_INCREMENT PRIMARY KEY,
    store_id        INT NOT NULL,
    product_id      INT NOT NULL,
    qty_on_hand     INT NOT NULL DEFAULT 0,
    reorder_level   INT NOT NULL DEFAULT 10,
    last_restock    DATE,
    UNIQUE KEY uq_store_product (store_id, product_id),
    FOREIGN KEY (store_id) REFERENCES stores(store_id),
    FOREIGN KEY (product_id) REFERENCES products(product_id)
);