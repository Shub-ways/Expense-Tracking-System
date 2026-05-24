import streamlit as st
import requests
from utils import API_URL
from analytics_by_category import analytics_by_category_tab
from analytics_by_months import analytics_by_months_tab
from add_update import add_update_tab
from budget import budget_tab

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
            login_submitted = st.form_submit_button("Log In", use_container_width=True)

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
                    except Exception:
                        st.error("Could not connect to the backend server. Please verify it is running.")

    with auth_tab2:
        st.subheader("Create a new account")
        with st.form("register_form"):
            new_username = st.text_input("Username")
            new_password = st.text_input("Password", type="password")
            confirm_password = st.text_input("Confirm Password", type="password")
            register_submitted = st.form_submit_button("Register", use_container_width=True)

            if register_submitted:
                if not new_username or not new_password:
                    st.error("Please fill in all fields")
                elif new_password != confirm_password:
                    st.error("Passwords do not match")
                elif len(new_password) < 6:
                    st.error("Password must be at least 6 characters long")
                else:
                    try:
                        resp = requests.post(
                            f"{API_URL}/auth/register",
                            json={"username": new_username, "password": new_password},
                        )
                        if resp.status_code == 200:
                            st.success("Account created successfully! Please log in.")
                        else:
                            st.error(resp.json().get("detail", "Failed to register"))
                    except Exception:
                        st.error("Could not connect to the backend server. Please verify it is running.")

else:
    # Sidebar layout for profile information and log out button
    with st.sidebar:
        st.markdown(f"### 👤 Logged in as: **{st.session_state['username']}**")
        st.markdown("---")
        if st.button("🚪 Log Out", use_container_width=True):
            del st.session_state["token"]
            del st.session_state["username"]
            st.rerun()

    st.markdown("<h1 class='main-title'>💸 Expense Tracking System</h1>", unsafe_allow_html=True)
    st.markdown(
        f"<p class='main-subtitle'>Welcome back, <b>{st.session_state['username']}</b>! Track your personal finances.</p>",
        unsafe_allow_html=True,
    )

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