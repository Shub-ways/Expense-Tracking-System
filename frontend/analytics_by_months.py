import streamlit as st 
import requests
import pandas as pd
import plotly.express as px
from utils import API_URL, get_auth_headers, format_currency

def analytics_by_months_tab():
    st.markdown("### Expense Breakdown By Months")
    
    payload = {} 
        
    try:
        response = requests.post(f"{API_URL}/analytics/month", json=payload, headers=get_auth_headers())
        if response.status_code != 200:
            st.error("Failed to load monthly analytics. Is the backend running?")
            return
            
        response_data = response.json()
            
        data = {
                "Month": list(response_data.keys()),
                "Total": [response_data[month]["total"] for month in response_data]
            }
        df = pd.DataFrame(data)
            
        month_order = [
                "January", "February", "March", "April", "May", "June", 
                "July", "August", "September", "October", "November", "December"
            ]
            
        df["Month"] = pd.Categorical(df["Month"], categories=month_order, ordered=True)
            
        df_sorted = df.sort_values(by="Month", ascending=True)
            
        symbol = st.session_state.get("currency", "₹")
        fig = px.area(
            df_sorted,
            x="Month",
            y="Total",
            markers=True,
            color_discrete_sequence=["#3B82F6"]
        )
        fig.update_traces(
            hovertemplate=f"<b>%{{x}}</b><br>Total Spent: {symbol}%{{y:,.2f}}"
        )
        fig.update_layout(
            xaxis_title="Month",
            yaxis_title=f"Total Expenses ({symbol})",
            margin=dict(t=20, b=20, l=20, r=20),
            height=350
        )
        st.plotly_chart(fig, use_container_width=True)
            
        df_display = df_sorted.copy()
        df_display["Total"] = df_display["Total"].apply(format_currency)
            
        st.dataframe(df_display, use_container_width=True)

        # CSV Export
        csv = df_display.to_csv(index=False).encode("utf-8")
        st.download_button(
            "📥 Download as CSV",
            data=csv,
            file_name="monthly_expenses.csv",
            mime="text/csv",
        )
            
    except Exception as e:
        st.error("Error fetching data. Please check if backend is running.")
        st.write(e)