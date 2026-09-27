# Product Analytics page

import sys
from pathlib import Path

import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from src.analytics import get_profit_margins, get_top_products, get_daily_patterns

st.set_page_config(page_title="Product Analytics", page_icon="🛍️", layout="wide")

st.markdown("# 🛍️ Product Analytics")
st.markdown("Best sellers, profit margins, and shopping patterns.")
st.markdown("---")

# Top products
top = get_top_products(15)

fig = px.bar(
    top.sort_values("revenue", ascending=True),
    x="revenue", y="product_name", orientation="h", color="category",
    title="Top 15 Products by Revenue",
    color_discrete_sequence=px.colors.qualitative.Set2,
)
fig.update_layout(
    template="plotly_dark", paper_bgcolor="rgba(0,0,0,0)",
    height=500, yaxis_title="",
)
st.plotly_chart(fig, use_container_width=True)

# Profit margins and daily patterns
col1, col2 = st.columns(2)

margins = get_profit_margins(10)

with col1:
    st.markdown("### Profit Margins")
    fig2 = go.Figure(go.Bar(
        x=margins["margin_pct"], y=margins["product_name"],
        orientation="h",
        marker=dict(color=margins["margin_pct"], colorscale="RdYlGn", cmin=0, cmax=80),
        text=margins["margin_pct"].apply(lambda x: f"{x:.1f}%"),
        textposition="outside",
    ))
    fig2.update_layout(
        template="plotly_dark", paper_bgcolor="rgba(0,0,0,0)",
        height=420, yaxis_title="", xaxis_title="Margin %",
    )
    st.plotly_chart(fig2, use_container_width=True)

with col2:
    st.markdown("### Orders by Day of Week")
    patterns = get_daily_patterns()
    fig3 = go.Figure()
    fig3.add_trace(go.Bar(
        x=patterns["day_name"], y=patterns["orders"],
        name="Orders", marker_color="#00d2ff",
    ))
    fig3.add_trace(go.Scatter(
        x=patterns["day_name"], y=patterns["revenue"],
        name="Revenue", yaxis="y2",
        mode="lines+markers",
        line=dict(color="#ff6b6b", width=3), marker=dict(size=8),
    ))
    fig3.update_layout(
        template="plotly_dark", paper_bgcolor="rgba(0,0,0,0)",
        height=420,
        yaxis=dict(title="Orders"),
        yaxis2=dict(title="Revenue (₹)", overlaying="y", side="right"),
        legend=dict(orientation="h", y=1.12),
    )
    st.plotly_chart(fig3, use_container_width=True)
