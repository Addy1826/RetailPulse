# app.py - Main Streamlit dashboard (Executive Overview page)

import sys
from pathlib import Path

import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

sys.path.insert(0, str(Path(__file__).resolve().parent))

from src.analytics import (
    get_category_revenue, get_monthly_revenue,
    get_revenue_kpis, get_total_products, get_total_stores,
)

st.set_page_config(
    page_title="RetailPulse",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom styling
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
    html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
    .main .block-container { padding-top: 2rem; max-width: 1200px; }
    .kpi-card {
        background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
        border-radius: 16px; padding: 1.5rem; text-align: center;
        border: 1px solid rgba(255,255,255,0.06);
        box-shadow: 0 8px 32px rgba(0,0,0,0.3);
    }
    .kpi-value {
        font-size: 2.2rem; font-weight: 700;
        background: linear-gradient(135deg, #00d2ff, #7b2ff7);
        -webkit-background-clip: text; -webkit-text-fill-color: transparent;
    }
    .kpi-label {
        font-size: 0.85rem; color: #8892b0;
        text-transform: uppercase; letter-spacing: 1.5px;
    }
    div[data-testid="stSidebar"] {
        background: linear-gradient(180deg, #0d1117 0%, #161b22 100%);
    }
</style>
""", unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.markdown("## 📊 RetailPulse")
    st.markdown("---")
    st.markdown("**Retail Analytics Dashboard**")
    st.markdown(
        "Navigate using the pages:\n"
        "- 🏪 Store Performance\n"
        "- 🛍️ Product Analytics\n"
        "- 👥 Customer Insights\n"
        "- 📦 Inventory Monitor"
    )
    st.markdown("---")
    st.caption("Streamlit + Plotly + MySQL")

# Header
st.markdown("# 📊 Executive Overview")
st.markdown("Real-time retail performance at a glance.")
st.markdown("---")

# KPI Cards
kpis = get_revenue_kpis()

cols = st.columns(4)
kpi_items = [
    (f"₹{kpis.get('total_revenue', 0):,.0f}", "Total Revenue"),
    (f"{int(kpis.get('total_orders', 0)):,}", "Total Orders"),
    (f"₹{kpis.get('avg_order_value', 0):,.0f}", "Avg Order Value"),
    (f"{int(kpis.get('unique_customers', 0)):,}", "Active Customers"),
]

for col, (value, label) in zip(cols, kpi_items):
    col.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-value">{value}</div>
            <div class="kpi-label">{label}</div>
        </div>
    """, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# Monthly revenue chart
monthly = get_monthly_revenue()

fig_trend = go.Figure()
fig_trend.add_trace(go.Scatter(
    x=monthly["month"], y=monthly["revenue"],
    mode="lines+markers",
    line=dict(color="#00d2ff", width=3),
    marker=dict(size=6, color="#7b2ff7"),
    fill="tozeroy",
    fillcolor="rgba(0,210,255,0.08)",
    name="Revenue",
))
fig_trend.update_layout(
    title="Monthly Revenue Trend",
    xaxis_title="Month", yaxis_title="Revenue (₹)",
    template="plotly_dark",
    paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
    height=400, margin=dict(l=40, r=20, t=50, b=40),
)
st.plotly_chart(fig_trend, use_container_width=True)

# Category charts
col1, col2 = st.columns(2)
cat_rev = get_category_revenue()

with col1:
    fig_pie = px.pie(
        cat_rev, values="revenue", names="category",
        title="Revenue by Category", hole=0.45,
        color_discrete_sequence=px.colors.sequential.Plasma_r,
    )
    fig_pie.update_layout(
        template="plotly_dark", paper_bgcolor="rgba(0,0,0,0)",
        height=400, margin=dict(l=20, r=20, t=50, b=20),
    )
    st.plotly_chart(fig_pie, use_container_width=True)

with col2:
    fig_bar = px.bar(
        cat_rev.sort_values("units_sold", ascending=True),
        x="units_sold", y="category", orientation="h",
        title="Units Sold by Category",
        color="units_sold", color_continuous_scale="Viridis",
    )
    fig_bar.update_layout(
        template="plotly_dark", paper_bgcolor="rgba(0,0,0,0)",
        height=400, showlegend=False, margin=dict(l=20, r=20, t=50, b=20),
    )
    fig_bar.update_coloraxes(showscale=False)
    st.plotly_chart(fig_bar, use_container_width=True)

st.markdown("---")
st.caption("RetailPulse - Data refreshed from MySQL in real time.")
