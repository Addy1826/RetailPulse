# RetailPulse 📊

**End-to-End Retail Sales & Inventory Analytics Platform**

An end-to-end data engineering and analytics project featuring synthetic data generation, Pandas data cleaning and validation, MySQL relational warehousing, SQL analytics queries, and an interactive multi-page Streamlit dashboard.

🌐 **Live Dashboard**: [https://addy1826-retailpulse-app-vvgkvb.streamlit.app/](https://addy1826-retailpulse-app-vvgkvb.streamlit.app/)

---

## 🏗️ Architecture

```
Raw CSVs (Faker) ──> Pandas Cleaning ──> Validation ──> MySQL / SQLite ──> SQL Analytics ──> Streamlit Dashboard
```

```
RetailPulse/
├── app.py                         # Streamlit entry — Executive Overview
├── pages/                         # Multi-page dashboard
│   ├── 1_🏪_Store_Performance.py   # Store & city sales breakdown
│   ├── 2_🛍️_Product_Analytics.py   # Best sellers & profit margins
│   ├── 3_👥_Customer_Insights.py   # Customer spending & payment methods
│   └── 4_📦_Inventory_Monitor.py   # Stock levels & low-stock alerts
├── src/                           # Core modules
│   ├── analytics.py               # SQL queries & DataFrame functions
│   ├── cleaning.py                # Pandas cleaning pipeline
│   ├── database.py                # Database connection (MySQL + SQLite fallback)
│   └── validation.py              # Data integrity & validation checks
├── scripts/                       # Pipeline CLI scripts
│   ├── generate_data.py           # Synthetic data generator (Faker)
│   ├── clean_data.py              # Clean and validate raw CSVs
│   ├── load_database.py           # Apply schema & load into MySQL
│   └── build_sqlite_db.py         # Build SQLite database bundle for deployment
├── sql/
│   ├── schema.sql                 # 6-table relational schema
│   └── analytics_queries.sql      # 12 standalone analytics SQL queries
├── data/
│   ├── raw/                       # Generated raw CSV files
│   ├── processed/                 # Cleaned CSV files
│   └── retailpulse.db             # Bundled SQLite database
├── tests/
│   └── test_pipeline.py           # Pytest test suite (20 tests)
├── .env.example                   # MySQL environment template
├── .streamlit/config.toml         # Theme settings
└── requirements.txt               # Project dependencies
```

---

## 📊 Database Schema

The database consists of **6 normalized relational tables**:

```
Customers ──┐
             ├──> orders ──> order_items <── products
stores ──────┘                     │
                                   ↓
                               inventory
```

| Table | Primary Key | Foreign Keys | Description |
|-------|-------------|--------------|-------------|
| `Customers` | `Customer_Id` | — | Customer details (`Customer_name`, `email`, `city`, `signup_date`) |
| `stores` | `store_id` | — | Retail store locations (`store_name`, `city`, `openinig_date`) |
| `products` | `product_id` | — | Catalog items (`product_name`, `category`, `Unit_price`, `recorder_level`) |
| `orders` | `order_id` | `Customer_id`, `store_id` | Orders header (`Order_date`, `payment_method`, `order_status`) |
| `order_items` | `(order_id, product_id)` | `order_id`, `product_id` | Line items with `quantity` and `selling_price` |
| `inventory` | `(store_id, product_id)` | `store_id`, `product_id` | Stock quantity and last restock date per store & product |

---

## 🔑 Key Analytics Queries

The project includes **12 standalone SQL analytics queries** in [`sql/analytics_queries.sql`](sql/analytics_queries.sql):

1. **Overall Sales KPIs**: Total revenue, completed orders, unique customers, and average order value.
2. **Monthly Sales Trend**: Revenue and order volume grouped by month.
3. **Top 10 Best-Selling Products**: Products with highest revenue and units sold.
4. **Revenue by Category**: Sales volume and revenue across retail categories.
5. **Revenue by Store**: Store-level revenue and transaction count.
6. **Customer Sales by City**: Customer distribution and revenue by city.
7. **Payment Method Breakdown**: Distribution of payment methods (UPI, Cards, Cash).
8. **Top Spending Customers**: Highest customer lifetime value rankings.
9. **Low-Stock Inventory Alerts**: Items where `stock_quantity < recorder_level`.
10. **Store Performance Leaderboard**: Ranking stores by revenue, orders, and unique customers.
11. **Most Profitable Products**: Comparing `selling_price` against `Unit_price` to find top gross margins.
12. **Day-of-Week Shopping Patterns**: Identifying peak shopping days across the week.

---

## ⚙️ Setup & Installation

### Prerequisites
- **Python 3.10+**
- **MySQL 8.0+** (optional for local warehousing; SQLite fallback bundled for instant use)

### 1. Clone & Set Up Virtual Environment

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

To regenerate data and load into MySQL from scratch:

```bash
# 1. Generate raw data
python scripts/generate_data.py

# 2. Clean and validate data
python scripts/clean_data.py

# 3. Load schema and data into MySQL
python scripts/load_database.py
```

---

## 🖥️ Launch the Streamlit Dashboard

```bash
streamlit run app.py
```

Open **http://localhost:8501** in your browser to view the dashboard:

| Page | Features |
|------|----------|
| **Executive Overview** | Real-time KPI metric cards, monthly trend chart, category revenue pie chart |
| **Store Performance** | Store leaderboard, revenue by city, store comparison |
| **Product Analytics** | Top 15 products by revenue, profit margin analysis, day-of-week patterns |
| **Customer Insights** | City revenue breakdown, payment method distribution, top customer LTV |
| **Inventory Monitor** | Stock levels by category, automatic low-stock reorder warnings |

---

## 🧪 Testing

Run the test suite with pytest:

```bash
pytest tests/ -v
```

Covers:
- Raw CSV generation checks
- Cleaning rules (deduplication, positive pricing, quantity bounds)
- Pre-load data validation
- Database table row counts
- Analytics query correctness

---

## 🌐 Deployment

The dashboard is deployed on **Streamlit Community Cloud** with automatic database fallback:
- **Cloud URL**: [https://addy1826-retailpulse-app-vvgkvb.streamlit.app/](https://addy1826-retailpulse-app-vvgkvb.streamlit.app/)
- When deployed on the cloud without a local MySQL server, [`src/database.py`](src/database.py) automatically uses [`data/retailpulse.db`](data/retailpulse.db) with custom date/time functions for 100% feature parity.

---

## 🛠 Tech Stack

- **Language**: Python 3.14
- **Database**: MySQL 8.0 / SQLite
- **Data Processing**: Pandas, NumPy
- **Database Connector**: SQLAlchemy, PyMySQL
- **Visualization**: Plotly, Streamlit
- **Data Generation**: Faker
- **Testing**: pytest
