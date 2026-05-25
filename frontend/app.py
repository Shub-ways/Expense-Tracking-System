import streamlit as st
import requests
from utils import API_URL, get_auth_headers
from analytics_by_category import analytics_by_category_tab
from analytics_by_months import analytics_by_months_tab
from add_update import add_update_tab
from budget import budget_tab
from search_filter import search_filter_tab


st.set_page_config(
    page_title="Expense Tracker",
    page_icon="💸",
    layout="wide",
)

# Custom premium styling
st.markdown(
    """
    <style>
    .main-title {
        font-size: 2.8rem;
        font-weight: 700;
        color: #1E293B;
        margin-bottom: 0.2rem;
    }
    .main-subtitle {
        font-size: 1.1rem;
        color: #64748B;
        margin-bottom: 2rem;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

if "token" not in st.session_state:
    st.markdown("<h1 class='main-title'>💸 Expense Tracking System</h1>", unsafe_allow_html=True)
    st.markdown("<p class='main-subtitle'>Access your personal finance manager</p>", unsafe_allow_html=True)

    auth_tab1, auth_tab2 = st.tabs(["🔐 Log In", "👤 Register"])

    with auth_tab1:
        st.subheader("Login to your account")
        with st.form("login_form"):
            username = st.text_input("Username")
            password = st.text_input("Password", type="password")
            login_submitted = st.form_submit_button("Log In", width="stretch")

            if login_submitted:
                if not username or not password:
                    st.error("Please enter both username and password")
                else:
                    try:
                        resp = requests.post(
                            f"{API_URL}/auth/login",
                            json={"username": username, "password": password},
                        )
                        if resp.status_code == 200:
                            data = resp.json()
                            st.session_state["token"] = data["access_token"]
                            st.session_state["username"] = username
                            st.success("Logged in successfully!")
                            st.rerun()
                        else:
                            st.error(resp.json().get("detail", "Invalid credentials"))
                    except Exception as e:
                        st.error(f"Could not connect to the backend server at {API_URL}. Please verify it is running. (Error: {e})")

    with auth_tab2:
        st.subheader("Create a new account")
        with st.form("register_form"):
            new_username = st.text_input("Username")
            new_email = st.text_input("Email Address")
            new_password = st.text_input("Password", type="password")
            confirm_password = st.text_input("Confirm Password", type="password")
            register_submitted = st.form_submit_button("Register", width="stretch")

            if register_submitted:
                if not new_username or not new_email or not new_password:
                    st.error("Please fill in all fields")
                elif "@" not in new_email:
                    st.error("Please enter a valid email address")
                elif new_password != confirm_password:
                    st.error("Passwords do not match")
                elif len(new_password) < 6:
                    st.error("Password must be at least 6 characters long")
                else:
                    try:
                        resp = requests.post(
                            f"{API_URL}/auth/register",
                            json={"username": new_username, "email": new_email, "password": new_password},
                        )
                        if resp.status_code == 200:
                            st.success("Account created successfully! Please log in.")
                        else:
                            st.error(resp.json().get("detail", "Failed to register"))
                    except Exception as e:
                        st.error(f"Could not connect to the backend server at {API_URL}. Please verify it is running. (Error: {e})")

else:
    # Fetch currency symbol on login
    if "currency" not in st.session_state:
        try:
            resp = requests.get(f"{API_URL}/auth/currency", headers=get_auth_headers())
            if resp.status_code == 200:
                st.session_state["currency"] = resp.json()["currency"]
            else:
                st.session_state["currency"] = "₹"
        except Exception:
            st.session_state["currency"] = "₹"

    # Sidebar layout for profile information, settings, and log out button
    with st.sidebar:
        st.markdown(f"### 👤 Logged in as: **{st.session_state['username']}**")
        st.markdown("---")
        
        st.markdown("### ⚙️ Preferences")
        curr_options = ["₹", "$", "€", "£"]
        try:
            curr_idx = curr_options.index(st.session_state.get("currency", "₹"))
        except ValueError:
            curr_idx = 0
            
        selected_curr = st.selectbox("Preferred Currency", curr_options, index=curr_idx)
        if selected_curr != st.session_state.get("currency"):
            try:
                resp = requests.put(
                    f"{API_URL}/auth/currency",
                    json={"currency": selected_curr},
                    headers=get_auth_headers()
                )
                if resp.status_code == 200:
                    st.session_state["currency"] = selected_curr
                    st.toast(f"Currency updated to {selected_curr}")
                    st.rerun()
                else:
                    st.error(f"Failed to save currency preference: Status {resp.status_code} - {resp.text}")
            except Exception as e:
                st.error(f"Failed to save currency preference: {e}")

        st.markdown("---")
        
        # Dark Mode Toggle
        st.markdown("### 🎨 Appearance")
        dark_mode = st.toggle("🌙 Dark Mode", value=st.session_state.get("dark_mode", False))
        if dark_mode != st.session_state.get("dark_mode"):
            st.session_state["dark_mode"] = dark_mode
            st.rerun()

        st.markdown("---")
        if st.button("🚪 Log Out", width="stretch"):
            del st.session_state["token"]
            del st.session_state["username"]
            if "currency" in st.session_state:
                del st.session_state["currency"]
            st.rerun()

    # Apply Dark Mode CSS if enabled
    if st.session_state.get("dark_mode", False):
        st.markdown(
            """
            <style>
            [data-testid="stAppViewContainer"] {
                background-color: #0F172A;
                color: #F8FAFC;
            }
            [data-testid="stSidebar"] {
                background-color: #1E293B !important;
            }
            .main-title, .main-subtitle {
                color: #F8FAFC !important;
            }
            .stMarkdown p {
                color: #F8FAFC;
            }
            /* Override for tabs and select boxes in dark mode */
            .stTabs [data-baseweb="tab-list"] button [data-testid="stMarkdownContainer"] p {
                color: #94A3B8;
            }
            .stTabs [data-baseweb="tab-list"] button[aria-selected="true"] [data-testid="stMarkdownContainer"] p {
                color: #F8FAFC;
            }
            </style>
            """,
            unsafe_allow_html=True,
        )

    st.markdown("<h1 class='main-title'>💸 Expense Tracking System</h1>", unsafe_allow_html=True)
    st.markdown(
        f"<p class='main-subtitle'>Welcome back, <b>{st.session_state['username']}</b>! Track your personal finances.</p>",
        unsafe_allow_html=True,
    )

    # Fetch budget vs actual alerts for warning banners
    from datetime import date
    today = date.today()
    try:
        alert_resp = requests.get(
            f"{API_URL}/budgets/vs-actual",
            params={"year": today.year, "month": today.month},
            headers=get_auth_headers()
        )
        if alert_resp.status_code == 200:
            budget_report = alert_resp.json()
            alerts = []
            for category, info in budget_report.items():
                pct = info["percentage_used"]
                limit = info["monthly_limit"]
                spent = info["spent"]
                if limit > 0:
                    symbol = st.session_state.get("currency", "₹")
                    if spent > limit:
                        alerts.append(f"🚨 **{category}**: Budget exceeded! Spent {symbol}{spent:,.2f} of {symbol}{limit:,.2f} ({pct:.1f}% used)")
                    elif pct >= 80:
                        alerts.append(f"⚠️ **{category}**: Near budget limit! Spent {symbol}{spent:,.2f} of {symbol}{limit:,.2f} ({pct:.1f}% used)")
            
            if alerts:
                with st.expander("🔔 Spending Alerts", expanded=True):
                    for alert in alerts:
                        if "🚨" in alert:
                            st.error(alert)
                        else:
                            st.warning(alert)
    except Exception:
        pass

    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "📝 Add / Update",
        "📊 Analytics by Category",
        "📅 Analytics by Month",
        "💰 Budget",
        "🔍 Search & Filters",
    ])

    with tab1:
        add_update_tab()
    with tab2:
        analytics_by_category_tab()
    with tab3:
        analytics_by_months_tab()
    with tab4:
        budget_tab()
    with tab5:
        search_filter_tab()