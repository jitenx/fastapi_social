import streamlit as st
import time
from core.auth import require_auth, logout
from core.api import get, put, delete
from ui.sidebar import render_sidebar

require_auth()
render_sidebar()
st.title("User Profile")

user = get("/users/profile/me")

st.info(f"""
Name: {user['first_name']} {user['last_name']}
Email: {user['email']}
""")

if st.button("✏️ Update Profile"):
    st.session_state["edit_user"] = user

confirm = st.checkbox("I understand this will delete my account")
if st.button("🛑 Delete Account", disabled=not confirm):
    delete(f"/users/{user['id']}")
    logout()

if "edit_user" in st.session_state:
    u = st.session_state["edit_user"]

    with st.form("update_user"):
        first = st.text_input("First Name", u["first_name"])
        last = st.text_input("Last Name", u["last_name"])
        email=st.text_input("Email", u["email"],disabled=True)
        password = st.text_input("New Password", type="password")
        save = st.form_submit_button("Save")
        cancel = st.form_submit_button("Cancel")

    if cancel:
        del st.session_state["edit_user"]
        st.rerun()

    if save:
        if not all([first, last, password]):
            st.error("All fields required")
        else:
            put(f"/users/{u['id']}", {
                "first_name": first,
                "last_name": last,
                "email":email,
                "password": password
            })
            st.success("Profile updated — please login again")
            time.sleep(2)
            logout()