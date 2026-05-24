import streamlit as st

import os

API_URL = os.getenv("API_URL", "http://127.0.0.1:8000")

def get_auth_headers():
    """Return headers containing the Bearer token if the user is logged in."""
    headers = {}
    if "token" in st.session_state:
        headers["Authorization"] = f"Bearer {st.session_state['token']}"
    return headers
