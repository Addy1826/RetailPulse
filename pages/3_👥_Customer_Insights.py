# Customer Insights page

import sys
from pathlib import Path

import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from src.analytics import get_customer_segments, get_payment_methods, get_top_customers

st.set_page_config(page_title="Customer Insights", page_icon="👥", layout="wide")

st.markdown("# 👥 Customer Insights")
st.markdown("Segments, lifetime value, and payment preferences.")
st.markdown("---")

# Segments / Cities
segments = get_customer_segments()
col1, col2 = st.columns(2)

with col1:
    fig = px.bar(
        segments, x="segment", y="revenue",
        title="Revenue by City",
        color="segment", text_auto=",.0f",
        color_discrete_sequence=px.colors.qualitative.Plotly,
    )
    fig.update_layout(
        template="plotly_dark", paper_bgcolor="rgba(0,0,0,0)",
        height=380, yaxis_title="Revenue (₹)", xaxis_title="City",
        showlegend=False,
    )
    st.plotly_chart(fig, use_container_width=True)

with col2:
    fig2 = px.bar(
        segments, x="segment", y="revenue_per_customer",
        title="Revenue per Customer by City",
        color="segment", text_auto=",.0f",
        color_discrete_sequence=px.colors.qualitative.Plotly,
    )
    fig2.update_layout(
        template="plotly_dark", paper_bgcolor="rgba(0,0,0,0)",
        height=380, yaxis_title="₹ per Customer", xaxis_title="City",
        showlegend=False,
    )
    st.plotly_chart(fig2, use_container_width=True)

# Payment methods
st.markdown("### Payment Methods")
payments = get_payment_methods()
fig3 = px.pie(
    payments, values="total_amount", names="payment_method",
    hole=0.45, color_discrete_sequence=px.colors.sequential.Tealgrn_r,
)
fig3.update_layout(
    template="plotly_dark", paper_bgcolor="rgba(0,0,0,0)", height=380,
)
st.plotly_chart(fig3, use_container_width=True)

# Top customers
st.markdown("### Top Customers by Lifetime Value")
top_cust = get_top_customers(15)

st.dataframe(
    top_cust.style.format({
        "lifetime_value": "₹{:,.0f}",
        "total_orders": "{:,}",
    }).background_gradient(subset=["lifetime_value"], cmap="plasma"),
    use_container_width=True,
    height=450,
)
