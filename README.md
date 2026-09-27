# RetailPulse 📊

**Retail Sales & Inventory Analytics Platform**

An end-to-end relational database and SQL analytics project demonstrating database design, data cleaning and validation with Pandas, business-driven SQL querying, and an interactive Streamlit dashboard.

🌐 **Live Dashboard**: [https://addy1826-retailpulse-app-vvgkvb.streamlit.app/](https://addy1826-retailpulse-app-vvgkvb.streamlit.app/)

---

## 🏗️ Architecture

```
Raw CSVs (Faker) ──> Pandas Cleaning & Validation ──> MySQL / SQLite ──> SQL Analytics ──> Streamlit Dashboard
```

```
RetailPulse/
├── app.py                         # Streamlit entry — Executive Overview
├── pages/                         # Multi-page dashboard
│   ├── 1_🏪_Store_Performance.py   # Store & city sales breakdown
│   ├── 2_🛍️_Product_Analytics.py   # Top products & estimated gross margins
│   ├── 3_👥_Customer_Insights.py   # Customer spending & payment methods
│   └── 4_📦_Inventory_Monitor.py   # Stock levels & low-stock alerts
├── src/                           # Core modules
│   ├── analytics.py               # SQL queries & DataFrame functions
│   ├── cleaning.py                # Pandas cleaning pipeline
│   ├── database.py                # Database connection (MySQL + SQLite fallback with PRAGMA foreign_keys)
│   └── validation.py              # Data integrity & validation checks
├── scripts/                       # Pipeline CLI scripts
│   ├── generate_data.py           # Synthetic data generator (Faker)
│   ├── clean_data.py              # Clean and validate raw CSVs
│   ├── load_database.py           # Apply schema & load into MySQL
│   └── build_sqlite_db.py         # Build SQLite database bundle for deployment
├── sql/
│   ├── schema.sql                 # 6-table relational database schema
│   └── analytics_queries.sql      # 14 standalone analytics SQL queries
├── data/
│   ├── raw/                       # Generated raw CSV files
│   ├── processed/                 # Cleaned CSV files
│   └── retailpulse.db             # Bundled SQLite database
├── tests/
│   └── test_pipeline.py           # Pytest test suite (27 tests)
├── .env.example                   # MySQL environment template
├── .streamlit/config.toml         # Theme settings
└── requirements.txt               # Project dependencies
```

---

## 📊 Database Schema

The database consists of **6 normalized relational tables** designed to support store operations, order fulfillment, and inventory tracking:

```
Customers ──┐
             ├──> orders ──> order_items <── products
stores ──────┘                     │
                                   ↓
                               inventory
```

| Table | Primary Key | Foreign Keys | Key Constraints & Fields |
|-------|-------------|--------------|--------------------------|
| `Customers` | `Customer_Id` | — | `Customer_name` NOT NULL, `email` UNIQUE, `city`, `signup_date` |
| `stores` | `store_id` | — | `store_name` NOT NULL, `city` NOT NULL, `opening_date` |
| `products` | `product_id` | — | `product_name` NOT NULL, `category`, `Unit_price` CHECK (> 0), `reorder_level` DEFAULT 10 |
| `orders` | `order_id` | `Customer_id`, `store_id` | `Customer_id` NOT NULL, `store_id` NOT NULL, `Order_date` NOT NULL, `payment_method`, `order_status` |
| `order_items` | `(order_id, product_id)` | `order_id`, `product_id` | Composite PK, `quantity` CHECK (> 0), `selling_price` CHECK (> 0) |
| `inventory` | `(store_id, product_id)` | `store_id`, `product_id` | Composite PK, `stock_quantity` CHECK (>= 0), `last_updated` |

---

## 💡 SQL Concepts Demonstrated

The project demonstrates practical, production-level SQL concepts across schema design and analytical querying:

- **DDL & Constraints**: `CREATE TABLE`, `PRIMARY KEY`, composite primary keys, `FOREIGN KEY` references, `NOT NULL`, `UNIQUE`, `CHECK`, and `DEFAULT`.
- **Querying & Filtering**: `SELECT`, column aliasing, `WHERE` status and date filtering.
- **Joins**: Multi-table `INNER JOIN` across up to 4 tables; `LEFT JOIN` anti-join for finding records without matching entries (`WHERE right_table.id IS NULL`).
- **Aggregations & Grouping**: `COUNT`, `SUM`, `AVG`, `COUNT(DISTINCT)`, `GROUP BY` single and multiple columns, `HAVING` threshold filtering.
- **Mathematical Formulations**: True Average Order Value (AOV) calculated at the order level using `SUM(...) / NULLIF(COUNT(DISTINCT ...), 0)`.
- **Sorting & Pagination**: `ORDER BY` ascending and descending, `LIMIT` for top-N ranking.
- **Date Functions**: `DATE_FORMAT` for monthly aggregation, `DAYNAME` and `DAYOFWEEK` for sales patterns across days of the week.

---

## 🔑 Key Analytics Queries

The project contains **14 business-oriented SQL analytics queries** in [`sql/analytics_queries.sql`](sql/analytics_queries.sql):

1. **Executive Sales KPI Summary**: Total completed orders, total revenue, true Average Order Value (AOV = total revenue / completed orders), and unique purchasing customers.
2. **Monthly Revenue and Order Trend**: Monthly revenue and transaction volume using `DATE_FORMAT`.
3. **Top 10 Products by Revenue**: Highest grossing products ranked by revenue (`SUM(quantity * selling_price)`).
4. **Category Sales Performance**: Units sold and revenue breakdown across product categories.
5. **Store Revenue Performance**: Order counts and total revenue per retail store.
6. **Customer Revenue by City**: Customer count, order count, and revenue aggregated by customer city.
7. **Payment Method Performance**: Volume and total amount by payment method (UPI, Cards, Net Banking, Cash).
8. **Top 10 Customers by Completed-Order Spend**: Highest customer lifetime spending across completed orders.
9. **Low-Stock Inventory Alerts**: Active items where current stock is below the reorder point (`stock_quantity < reorder_level`).
10. **Store Performance Leaderboard**: Comprehensive store rankings comparing revenue, orders, and unique customers.
11. **Product Gross-Margin Analysis**: Compares total selling revenue against baseline cost (`Unit_price * quantity`) to calculate `estimated_gross_margin`.
12. **Day-of-Week Sales Pattern**: Evaluates shopping frequency and revenue by day of the week (`DAYNAME`, `DAYOFWEEK`).
13. **Repeat / High-Frequency Customers**: Demonstrates `HAVING` filtering by isolating customers with 6 or more completed orders.
14. **Customers With No Orders (Anti-Join)**: Demonstrates `LEFT JOIN` and `NULL` handling to identify registered customers who have not yet placed an order.

---

## ⚙️ Setup & Local Execution

### Prerequisites
- **Python 3.10+**
- **MySQL 8.0+** (optional for local warehousing; SQLite fallback is bundled for instant execution)

### 1. Clone & Set Up Environment

```bash
git clone https://github.com/Addy1826/RetailPulse.git
cd RetailPulse

python -m venv .venv
.venv\Scripts\activate        # Windows
# source .venv/bin/activate   # macOS / Linux

pip install -r requirements.txt
```

### 2. Configure Database Credentials (Optional for MySQL)

```bash
cp .env.example .env
# Edit .env with your MySQL root password if running local MySQL
```

---

## 🚀 Running the Data Pipeline

To generate synthetic data, clean it, and load it into the database:

```bash
# 1. Generate raw data
python scripts/generate_data.py

# 2. Clean and validate data
python scripts/clean_data.py

# 3. Apply schema and load into MySQL
python scripts/load_database.py

# 4. Rebuild SQLite deployment database
python scripts/build_sqlite_db.py
```

---

## 🖥️ Launch the Streamlit Dashboard

```bash
streamlit run app.py
```

Open **http://localhost:8501** in your browser:

| Page | Features |
|------|----------|
| **Executive Overview** | Real-time KPI metric cards (Revenue, Orders, true AOV, Customers), monthly trend, category revenue pie chart |
| **Store Performance** | Store leaderboard, revenue by city, store comparison |
| **Product Analytics** | Top 15 products by revenue, estimated gross margin analysis, day-of-week sales patterns |
| **Customer Insights** | City revenue breakdown, revenue per customer, payment method distribution, top customer LTV |
| **Inventory Monitor** | Stock levels by category, automatic low-stock reorder warnings |

---

## 🧪 Testing

Run the test suite with pytest:

```bash
pytest tests/ -v
```

The test suite (27 tests) verifies:
- Raw CSV generation and minimum row counts
- Cleaning logic (deduplication, positive pricing, quantity bounds)
- Pre-load data validation
- Database table existence and row counts
- Foreign key constraints and NOT NULL rules on `orders.Customer_id` and `orders.store_id`
- Composite primary key uniqueness on `order_items` and `inventory`
- SQLite `PRAGMA foreign_keys = 1` enforcement
- Mathematical equality of AOV (`total_revenue / completed_orders`)
- Execution of `HAVING` (repeat customers) and `LEFT JOIN` (anti-join) queries
- Query execution for low-stock alerts, monthly trends, top products, and estimated gross margin

---

## 🌐 Deployment

The dashboard is deployed on **Streamlit Community Cloud** with an automatic SQLite fallback:
- **Cloud URL**: [https://addy1826-retailpulse-app-vvgkvb.streamlit.app/](https://addy1826-retailpulse-app-vvgkvb.streamlit.app/)
- When deployed on the cloud without a local MySQL server, [`src/database.py`](src/database.py) automatically connects to [`data/retailpulse.db`](data/retailpulse.db) with SQLite foreign-key enforcement and custom date/time functions for 100% parity.

---

## 🛠 Tech Stack

- **Language**: Python 3.14
- **Database**: MySQL 8.0 / SQLite
- **Data Processing**: Pandas, NumPy
- **Database Connector**: SQLAlchemy, PyMySQL
- **Visualization**: Plotly, Streamlit
- **Data Generation**: Faker
- **Testing**: pytest
