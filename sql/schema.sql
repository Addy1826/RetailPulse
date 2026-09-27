CREATE DATABASE IF NOT EXISTS retailpulse;
USE retailpulse;

-- Drop tables in reverse dependency order
DROP TABLE IF EXISTS inventory;
DROP TABLE IF EXISTS order_items;
DROP TABLE IF EXISTS orders;
DROP TABLE IF EXISTS products;
DROP TABLE IF EXISTS stores;
DROP TABLE IF EXISTS Customers;

CREATE TABLE Customers (
    Customer_Id INT PRIMARY KEY,
    Customer_name VARCHAR(100) NOT NULL,
    email VARCHAR(150) UNIQUE,
    city VARCHAR(50),
    signup_date DATE
);

CREATE TABLE stores (
    store_id INT PRIMARY KEY,
    store_name VARCHAR(100) NOT NULL,
    city VARCHAR(50) NOT NULL,
    opening_date DATE
);

CREATE TABLE products (
    product_id INT PRIMARY KEY,
    product_name VARCHAR(120) NOT NULL,
    category VARCHAR(50) NOT NULL,
    Unit_price DECIMAL(10,2) CHECK (Unit_price > 0),
    reorder_level INT DEFAULT 10
);

CREATE TABLE orders (
    order_id INT PRIMARY KEY,
    Customer_id INT NOT NULL,
    store_id INT NOT NULL,
    Order_date DATE NOT NULL,
    payment_method VARCHAR(30),
    order_status VARCHAR(30),

    FOREIGN KEY (Customer_id)
        REFERENCES Customers(Customer_Id),

    FOREIGN KEY (store_id)
        REFERENCES stores(store_id)
);

CREATE TABLE order_items (
    order_id INT,
    product_id INT,
    quantity INT CHECK (quantity > 0),
    selling_price DECIMAL(10,2) CHECK (selling_price > 0),

    PRIMARY KEY (order_id, product_id),

    FOREIGN KEY (order_id)
        REFERENCES orders(order_id),

    FOREIGN KEY (product_id)
        REFERENCES products(product_id)
);

CREATE TABLE inventory (
    store_id INT,
    product_id INT,
    stock_quantity INT CHECK (stock_quantity >= 0),
    last_updated DATE,

    PRIMARY KEY (store_id, product_id),

    FOREIGN KEY (store_id)
        REFERENCES stores(store_id),

    FOREIGN KEY (product_id)
        REFERENCES products(product_id)
);