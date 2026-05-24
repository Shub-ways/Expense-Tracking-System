import streamlit as st

API_URL = "http://localhost:8000"

def get_auth_headers():
    """Return headers containing the Bearer token if the user is logged in."""
    headers = {}
    if "token" in st.session_state:
        headers["Authorization"] = f"Bearer {st.session_state['token']}"
    return headers
