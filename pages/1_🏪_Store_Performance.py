# Store Performance page

import sys
from pathlib import Path

import plotly.express as px
import streamlit as st

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from src.analytics import get_region_revenue, get_store_performance

st.set_page_config(page_title="Store Performance", page_icon="🏪", layout="wide")

st.markdown("# 🏪 Store Performance")
st.markdown("Revenue and order volume by store and region.")
st.markdown("---")

# Region charts
region = get_region_revenue()

col1, col2 = st.columns(2)

with col1:
    fig = px.bar(
        region, x="region", y="revenue",
        color="region", text_auto=",.0f",
        title="Revenue by Region",
        color_discrete_sequence=["#00d2ff", "#7b2ff7", "#ff6b6b", "#ffa94d"],
    )
    fig.update_layout(
        template="plotly_dark", paper_bgcolor="rgba(0,0,0,0)",
        height=380, showlegend=False,
    )
    st.plotly_chart(fig, use_container_width=True)

with col2:
    fig2 = px.pie(
        region, values="orders", names="region",
        title="Orders by Region", hole=0.4,
        color_discrete_sequence=["#00d2ff", "#7b2ff7", "#ff6b6b", "#ffa94d"],
    )
    fig2.update_layout(
        template="plotly_dark", paper_bgcolor="rgba(0,0,0,0)", height=380,
    )
    st.plotly_chart(fig2, use_container_width=True)

# Store leaderboard
st.markdown("### Store Leaderboard")
store_perf = get_store_performance()

st.dataframe(
    store_perf.style.format({
        "revenue": "₹{:,.0f}",
        "total_orders": "{:,}",
        "unique_customers": "{:,}",
    }).background_gradient(subset=["revenue"], cmap="viridis"),
    use_container_width=True,
    height=450,
)
