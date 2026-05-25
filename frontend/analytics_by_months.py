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
            
        month_order = [
            "January", "February", "March", "April", "May", "June", 
            "July", "August", "September", "October", "November", "December"
        ]
        
        data = {
            "Month": month_order,
            "Total": [response_data.get(m, {}).get("total", 0) for m in month_order]
        }
        
        df_sorted = pd.DataFrame(data)
            
        symbol = st.session_state.get("currency", "₹")
        fig = px.bar(
            df_sorted,
            x="Month",
            y="Total",
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
        st.plotly_chart(fig, width="stretch")
            
        df_display = df_sorted.copy()
        df_display["Total"] = df_display["Total"].apply(format_currency)
            
        st.dataframe(df_display, width="stretch")

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