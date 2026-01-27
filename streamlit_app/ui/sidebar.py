import streamlit as st
from core.auth import logout

def render_sidebar():
    if st.sidebar.button("➕ Create Post"):
        st.switch_page("pages/3_Create_Post.py")

    if st.sidebar.button("🚪 Sign out"):
        logout()