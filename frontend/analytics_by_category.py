import streamlit as st 
from datetime import datetime
import requests
import pandas as pd
import plotly.express as px
from utils import API_URL, get_auth_headers, format_currency

def analytics_by_category_tab():
    col1, col2 = st.columns(2)
    with col1:
        start_date = st.date_input("Start Date", datetime(2024, 8, 1))
    with col2:
        end_date = st.date_input("End Date", datetime(2024, 8, 5))
        
    if st.button("Get Analytics"):
        payload = {
            "start_date": start_date.strftime("%Y-%m-%d"),
            "end_date": end_date.strftime("%Y-%m-%d")
        }
        
        response = requests.post(f"{API_URL}/analytics/", json=payload, headers=get_auth_headers())
        if response.status_code != 200:
            st.error("Failed to load analytics data. Is the backend running?")
            return
            
        response_data = response.json()
        
        data = {
            "Category": list(response_data.keys()),
            "Total": [response_data[category]["total"] for category in response_data],
            "Percentage": [response_data[category]["percentage"] for category in response_data]
        }
        
        df = pd.DataFrame(data)
        df_sorted = df.sort_values(by="Percentage", ascending=False)
        
        st.markdown("### Expense Breakdown By Category")
        
        symbol = st.session_state.get("currency", "₹")
        fig = px.pie(
            df_sorted,
            names="Category",
            values="Total",
            hole=0.4,
            color_discrete_sequence=px.colors.qualitative.Pastel
        )
        fig.update_traces(
            textinfo='percent+label',
            hovertemplate=f"<b>%{{label}}</b><br>Spent: {symbol}%{{value:,.2f}}<br>Percentage: %{{percent}}"
        )
        fig.update_layout(
            showlegend=True,
            legend=dict(orientation="h", yanchor="bottom", y=-0.15, xanchor="center", x=0.5),
            margin=dict(t=20, b=20, l=20, r=20),
            height=400
        )
        st.plotly_chart(fig, use_container_width=True)
        
        df_display = df_sorted.copy()
        df_display["Total"] = df_display["Total"].apply(format_currency)
        df_display["Percentage"] = df_display["Percentage"].map("{:.2f}%".format)
        
        st.dataframe(df_display, use_container_width=True)

        # CSV Export
        csv = df_sorted.to_csv(index=False).encode("utf-8")
        st.download_button(
            "📥 Download as CSV",
            data=csv,
            file_name=f"expenses_{start_date}_to_{end_date}.csv",
            mime="text/csv",
        )