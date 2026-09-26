# Inventory Monitor page

import sys
from pathlib import Path

import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from src.analytics import get_inventory_summary, get_low_stock_alerts

st.set_page_config(page_title="Inventory Monitor", page_icon="📦", layout="wide")

st.markdown("# 📦 Inventory Monitor")
st.markdown("Stock levels and reorder alerts.")
st.markdown("---")

# Summary charts
summary = get_inventory_summary()
col1, col2 = st.columns(2)

with col1:
    fig = px.bar(
        summary.sort_values("total_stock", ascending=True),
        x="total_stock", y="category_name", orientation="h",
        title="Total Stock by Category",
        color="total_stock", color_continuous_scale="Viridis",
    )
    fig.update_layout(
        template="plotly_dark", paper_bgcolor="rgba(0,0,0,0)",
        height=420, showlegend=False,
    )
    fig.update_coloraxes(showscale=False)
    st.plotly_chart(fig, use_container_width=True)

with col2:
    fig2 = go.Figure(go.Bar(
        x=summary["category_name"],
        y=summary["low_stock_count"],
        marker=dict(color=summary["low_stock_count"], colorscale="Reds"),
        text=summary["low_stock_count"].astype(int),
        textposition="outside",
    ))
    fig2.update_layout(
        title="Low-Stock Alerts by Category",
        template="plotly_dark", paper_bgcolor="rgba(0,0,0,0)",
        height=420, yaxis_title="Items Below Reorder Level",
    )
    st.plotly_chart(fig2, use_container_width=True)

# Low stock table
st.markdown("### Items Below Reorder Level")
alerts = get_low_stock_alerts()

if alerts.empty:
    st.success("All products are above reorder levels!")
else:
    st.warning(f"{len(alerts)} product-store combinations need restocking.")
    st.dataframe(
        alerts.style.background_gradient(
            subset=["qty_on_hand"], cmap="RdYlGn", vmin=0, vmax=25
        ),
        use_container_width=True,
        height=500,
    )
