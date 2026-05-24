import streamlit as st
from analytics_by_category import analytics_by_category_tab
from analytics_by_months import analytics_by_months_tab
from add_update import add_update_tab
from budget import budget_tab

st.set_page_config(
    page_title="Expense Tracker",
    page_icon="💸",
    layout="wide",
)

st.title("💸 Expense Tracking System")
st.caption("Track your daily spending, analyse trends, and stay within budget.")

tab1, tab2, tab3, tab4 = st.tabs([
    "📝 Add / Update",
    "📊 Analytics by Category",
    "📅 Analytics by Month",
    "💰 Budget",
])

with tab1:
    add_update_tab()
with tab2:
    analytics_by_category_tab()
with tab3:
    analytics_by_months_tab()
with tab4:
    budget_tab()