import streamlit as st
from core.auth import logout

def render_sidebar():
    if st.sidebar.button("Feed"):
        st.switch_page("pages/1_All_Posts.py")
    if st.sidebar.button("My Posts"):
        st.switch_page("pages/2_My_Posts.py")
    if st.sidebar.button("➕ Create Post"):
        st.switch_page("pages/3_Create_Post.py")
    if st.sidebar.button("Update Profile"):
        st.switch_page("pages/4_User_Profile.py")

    if st.sidebar.button("🚪 Sign out"):
        logout()