import streamlit as st
import time
from core.auth import require_auth, logout
from core.api import get, put, delete
from ui.sidebar import render_sidebar

require_auth()
render_sidebar()

st.title("👤 User Profile")

# -------------------- TAB STATE --------------------
if "active_tab" not in st.session_state:
    st.session_state.active_tab = "Profile"

# Fetch user data
user = get("/users/profile/me")

# -------------------- TABS --------------------
tab1, tab2, tab3 = st.tabs(["Profile", "Edit Profile", "Delete Account"])

# -------------------- PROFILE --------------------
with tab1:
    st.info(f"""
**Name:** {user["first_name"]} {user["last_name"]}  
**Email:** {user["email"]}
""")

# -------------------- EDIT PROFILE --------------------
with tab2:
    st.subheader("✏️ Edit Profile")
    with st.form("update_user"):
        first_name = st.text_input("First Name", user["first_name"])
        last_name = st.text_input("Last Name", user["last_name"])
        email = st.text_input("Email", user["email"], disabled=True)
        new_password = st.text_input("New Password", type="password")

        col1, col2 = st.columns(2)
        save = col1.form_submit_button("💾 Save")
        # cancel = col2.form_submit_button("❌ Cancel")

    # if cancel:
    #     st.session_state.active_tab = "Profile"
    #     st.rerun()

    if save:
        if not all([first_name, last_name, new_password]):
            st.error("All fields are required")
        else:
            put(
                f"/users/{user['id']}",
                {
                    "first_name": first_name,
                    "last_name": last_name,
                    "email": email,
                    "password": new_password,
                },
            )
            st.success("✅ Profile updated — please login again")
            time.sleep(2)
            logout()

# -------------------- DELETE ACCOUNT --------------------
with tab3:
    st.error("🛑 This will permanently delete your account!")
    st.warning("This action cannot be undone")

    password = st.text_input("Confirm your password", type="password")
    confirm = st.checkbox("I understand this action is irreversible")

    col1, col2 = st.columns(2)
    # if col2.button("❌ Cancel"):
    #     st.session_state.active_tab = "Profile"
    #     st.rerun()

    if col1.button("🗑️ Yes, delete my account", disabled=not (confirm and password)):
        response = delete(f"/users/{user['id']}", {"password": password})
        if response.status_code == 204:
            st.success("✅ Account deleted")
            time.sleep(2)
            logout()
        else:
            st.error("❌ Incorrect password")
