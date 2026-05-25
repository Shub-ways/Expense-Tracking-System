import streamlit as st
from datetime import datetime, date
import requests
import pandas as pd
from utils import API_URL, get_auth_headers

CATEGORIES = ["Rent", "Food", "Shopping", "Entertainment", "Other"]


def budget_tab():
    st.markdown("## 💰 Budget Manager")
    st.markdown("Set monthly spending limits per category and track how you're doing.")

    # -----------------------------------------------------------------------
    # Section 1: Set / Update Budgets
    # -----------------------------------------------------------------------
    st.markdown("---")
    st.markdown("### ✏️ Set Monthly Budget Limits")

    with st.form("budget_form"):
        cols = st.columns(len(CATEGORIES))
        budget_inputs = {}
        for col, cat in zip(cols, CATEGORIES):
            with col:
                budget_inputs[cat] = st.number_input(
                    cat, min_value=0.0, step=100.0, value=0.0, key=f"budget_{cat}"
                )

        save_btn = st.form_submit_button("💾 Save Budgets")
        if save_btn:
            saved = 0
            for cat, limit in budget_inputs.items():
                if limit > 0:
                    resp = requests.post(
                        f"{API_URL}/budgets/",
                        json={"category": cat, "monthly_limit": limit},
                        headers=get_auth_headers(),
                    )
                    if resp.status_code == 200:
                        saved += 1
            if saved:
                st.success(f"✅ {saved} budget(s) saved successfully!")
            else:
                st.info("Enter at least one budget amount greater than 0.")

    # -----------------------------------------------------------------------
    # Section 2: Budget vs Actual
    # -----------------------------------------------------------------------
    st.markdown("---")
    st.markdown("### 📊 Budget vs Actual Spending")

    col1, col2 = st.columns(2)
    with col1:
        sel_year = st.number_input("Year", min_value=2020, max_value=2100, value=date.today().year, step=1)
    with col2:
        sel_month = st.selectbox(
            "Month",
            options=list(range(1, 13)),
            index=date.today().month - 1,
            format_func=lambda m: datetime(2000, m, 1).strftime("%B"),
        )

    if st.button("📈 Load Budget Report"):
        try:
            resp = requests.get(
                f"{API_URL}/budgets/vs-actual",
                params={"year": sel_year, "month": sel_month},
                headers=get_auth_headers(),
            )
            if resp.status_code != 200:
                st.error("Failed to load budget data. Is the backend running?")
                return

            data = resp.json()
            if not data:
                st.info("No budgets set yet. Use the form above to add some!")
                return

            # --- Progress bars ---
            symbol = st.session_state.get("currency", "₹")
            # --- Progress bars ---
            for cat, info in data.items():
                pct = min(info["percentage_used"], 100)
                color = "🔴" if info["over_budget"] else ("🟡" if pct > 75 else "🟢")
                st.markdown(f"**{color} {cat}**")
                if info["over_budget"]:
                    status_text = f"OVER BUDGET by {symbol}{abs(info['remaining']):.2f}"
                else:
                    status_text = f"{symbol}{info['remaining']:.2f} remaining"
                status = f"{symbol}{info['spent']:.2f} spent of {symbol}{info['monthly_limit']:.2f} ({status_text})"
                st.progress(pct / 100, text=status)

            st.markdown("---")

            # --- Summary table ---
            df = pd.DataFrame(
                [
                    {
                        "Category": cat,
                        f"Budget ({symbol})": f"{info['monthly_limit']:.2f}",
                        f"Spent ({symbol})": f"{info['spent']:.2f}",
                        f"Remaining ({symbol})": f"{info['remaining']:.2f}",
                        "% Used": f"{info['percentage_used']:.1f}%",
                        "Status": "⚠️ Over Budget" if info["over_budget"] else "✅ On Track",
                    }
                    for cat, info in data.items()
                ]
            )
            st.dataframe(df, width="stretch")

            # --- CSV Download ---
            csv = df.to_csv(index=False).encode("utf-8")
            month_name = datetime(2000, sel_month, 1).strftime("%B")
            st.download_button(
                "📥 Download Budget Report (CSV)",
                data=csv,
                file_name=f"budget_report_{sel_year}_{month_name}.csv",
                mime="text/csv",
            )

        except Exception as e:
            st.error(f"Error: {e}")
