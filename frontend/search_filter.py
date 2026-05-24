import streamlit as st
import requests
import pandas as pd
from datetime import date, timedelta
from utils import API_URL, get_auth_headers, format_currency

CATEGORIES = ["Rent", "Food", "Shopping", "Entertainment", "Other"]

def search_filter_tab():
    st.markdown("## 🔍 Search & Advanced Filtering")
    st.markdown("Query your historical expenses dynamically using advanced filters.")
    st.markdown("---")

    # Filter Controls
    col1, col2 = st.columns(2)
    with col1:
        start_date = st.date_input("Start Date", date.today() - timedelta(days=30))
        min_amount = st.number_input("Minimum Amount", min_value=0.0, value=0.0, step=10.0)
        category_sel = st.selectbox("Category", ["All"] + CATEGORIES)
    with col2:
        end_date = st.date_input("End Date", date.today())
        max_amount = st.number_input("Maximum Amount", min_value=0.0, value=100000.0, step=100.0)
        notes_query = st.text_input("Search Notes (keyword)")

    if st.button("🔍 Search Expenses", use_container_width=True):
        params = {}
        if start_date:
            params["start_date"] = start_date.strftime("%Y-%m-%d")
        if end_date:
            params["end_date"] = end_date.strftime("%Y-%m-%d")
        if category_sel != "All":
            params["category"] = category_sel
        if notes_query.strip():
            params["notes_query"] = notes_query.strip()
        if min_amount > 0:
            params["min_amount"] = min_amount
        if max_amount < 100000.0:
            params["max_amount"] = max_amount

        try:
            resp = requests.get(
                f"{API_URL}/expenses/search/all",
                params=params,
                headers=get_auth_headers()
            )
            if resp.status_code == 200:
                results = resp.json()
                if not results:
                    st.info("No matching expenses found for the selected criteria.")
                else:
                    # Parse to DataFrame
                    df = pd.DataFrame(results)
                    # Reorder columns for display
                    df = df[["expense_date", "category", "amount", "notes"]]
                    df.columns = ["Date", "Category", "Amount", "Notes"]
                    
                    # Create display version of DataFrame
                    df_display = df.copy()
                    df_display["Amount"] = df_display["Amount"].apply(format_currency)
                    
                    st.markdown(f"### Found {len(df)} matching expense(s)")
                    st.dataframe(df_display, use_container_width=True)

                    # Export to CSV
                    csv = df.to_csv(index=False).encode("utf-8")
                    st.download_button(
                        "📥 Download Results (CSV)",
                        data=csv,
                        file_name="expense_search_results.csv",
                        mime="text/csv",
                        use_container_width=True
                    )
            else:
                st.error("Failed to fetch search results from the backend.")
        except Exception as e:
            st.error(f"Error connecting to server: {e}")
