import streamlit as st 
import requests
import pandas as pd

API_URL = "http://localhost:8000"

def analytics_by_months_tab():
    st.title("Expense Breakdown By Months")
    
    payload = {} 
        
    try:
        response = requests.post(f"{API_URL}/analytics/month", json=payload)
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
            
        st.bar_chart(data=df_sorted.set_index("Month")['Total'], width=0, height=0, use_container_width=True)
            
        df_display = df_sorted.copy()
        df_display["Total"] = df_display["Total"].apply(lambda x: "{:.2f}".format(x))
            
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