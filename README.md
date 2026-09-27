# RetailPulse 📊

**Retail sales & inventory analytics** — an end-to-end data pipeline from synthetic CSV generation through Pandas cleaning, MySQL warehousing, SQL analysis, to an interactive Streamlit dashboard.

---

## 🏗️ Architecture

```
Raw CSVs (Faker) → Pandas Cleaning → Validation → MySQL → SQL Analytics → Streamlit Dashboard
```

```
RetailPulse/
├── app.py                     # Streamlit entry — Executive Overview
├── pages/                     # Multi-page dashboard
│   ├── 1_🏪_Store_Performance.py
│   ├── 2_🛍️_Product_Analytics.py
│   ├── 3_👥_Customer_Insights.py
│   └── 4_📦_Inventory_Monitor.py
├── src/                       # Core Python modules
│   ├── analytics.py           # Analytics functions (Python → MySQL → DataFrame)
│   ├── cleaning.py            # Pandas cleaning pipeline
│   ├── database.py            # SQLAlchemy connection + query helpers
│   └── validation.py          # Pre-load data validation
├── scripts/                   # CLI pipeline scripts
│   ├── generate_data.py       # Faker-based synthetic data generator
│   ├── clean_data.py          # Orchestrate cleaning + validation
│   └── load_database.py       # Load cleaned CSVs → MySQL
├── sql/
│   ├── schema.sql             # Full database schema (7 tables)
│   └── analytics_queries.sql  # 12 standalone analytics queries
├── data/
│   ├── raw/                   # Generated dirty CSVs
│   └── processed/             # Cleaned CSVs ready for MySQL
├── tests/
│   └── test_pipeline.py       # End-to-end pytest suite
├── .env.example               # Template for MySQL credentials
├── .streamlit/config.toml     # Dark theme config
└── requirements.txt
```

## ⚙️ Setup

### Prerequisites

- **Python 3.12+**
- **MySQL 8.0+** (running locally)

### Installation

```bash
# Clone and enter the project
cd RetailPulse

# Create virtual environment
python -m venv .venv
.venv\Scripts\activate        # Windows
# source .venv/bin/activate   # macOS/Linux

# Install dependencies
pip install -r requirements.txt

# Configure MySQL credentials
cp .env.example .env
# Edit .env with your MySQL root password
```

### Create the Database

```sql
CREATE DATABASE IF NOT EXISTS retailpulse;
```

---

## 🚀 Run the Pipeline

Execute the three scripts in order:

```bash
# 1. Generate ~22,000 rows of synthetic retail data (with intentional dirty data)
python scripts/generate_data.py

# 2. Clean data: dedup, type coercion, outlier capping, FK consistency
python scripts/clean_data.py

# 3. Apply schema + bulk-load into MySQL
python scripts/load_database.py
```

### Launch the Dashboard

```bash
streamlit run app.py
```

The dashboard opens at **http://localhost:8501** with four pages:

| Page | Content |
|------|---------|
| 📊 Executive Overview | KPI cards, monthly revenue trend, category breakdown |
| 🏪 Store Performance | Region revenue, store leaderboard |
| 🛍️ Product Analytics | Top products, profit margins, day-of-week patterns |
| 👥 Customer Insights | Segment analysis, payment methods, customer LTV |
| 📦 Inventory Monitor | Stock levels by category, low-stock alerts |

---

## 🧪 Testing

```bash
pytest tests/ -v
```

Covers: data generation checks, cleaning logic, validation rules, database integrity, and analytics query correctness.

---

## 📊 Database Schema

6 normalized tables with foreign key relationships:

```
Customers ──┐
             ├──→ orders ──→ order_items ←── products
stores ──────┘                     │
                                   ↓
                               inventory
```

| Table | Description |
|-------|-------------|
| `Customers` | Customer profiles (id, name, email, city, signup date) |
| `stores` | Store locations and opening dates |
| `products` | Product catalog with category, unit price, and reorder levels |
| `orders` | Transaction headers (date, payment method, order status) |
| `order_items` | Line items with quantity and selling price |
| `inventory` | Stock quantity per store and product |

---

## 🔑 Key Analytics Queries

The project includes **12 SQL analytics queries** covering:

1. Revenue KPIs (total, AOV, customer count)
2. Monthly revenue trends
3. Top products by revenue
4. Category revenue breakdown
5. Regional performance
6. Customer segment analysis
7. Payment method distribution
8. Customer lifetime value
9. Low-stock inventory alerts
10. Store performance leaderboard
11. Profit margin analysis
12. Day-of-week shopping patterns

---

## 🛠 Tech Stack

| Component | Technology |
|-----------|------------|
| Language | Python 3.12+ |
| Database | MySQL 8.0 |
| Data Processing | Pandas, NumPy |
| ORM / DB Access | SQLAlchemy + PyMySQL |
| Synthetic Data | Faker |
| Dashboard | Streamlit |
| Visualization | Plotly |
| Testing | pytest |

---

## 📁 Data Pipeline Details

### Generation (`generate_data.py`)
- Uses Faker with India locale for realistic names, cities, and states
- 10 product categories with brand-specific product names
- Intentionally injects ~3–5% dirty data: nulls, sentinel values, duplicate rows, outlier prices

### Cleaning (`cleaning.py` + `clean_data.py`)
- Strips whitespace, replaces sentinel strings with NaN
- Deduplicates on natural keys (email, SKU, order_id)
- Caps outlier prices at 98th percentile
- Validates ENUM values and coerces types
- Ensures FK consistency across all tables

### Validation (`validation.py`)
- Non-null checks on required columns
- Uniqueness checks on natural keys
- Foreign key integrity verification
- Domain-set validation for ENUM fields
- Positive-value checks for quantities and prices

---

© 2026 RetailPulse
