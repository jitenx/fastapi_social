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
Name: {user["first_name"]} {user["last_name"]}\n
Email: {user["email"]}
""")


# ---------- DELETE CONFIRMATION DIALOG ----------
# @st.dialog("Delete account")
# def confirm_delete_account(user_id):
#     st.error("🛑 This will permanently delete your account.")
#     st.warning("This action cannot be undone.")

#     confirm = st.checkbox("I understand the consequences")

#     col1, col2 = st.columns(2)

#     if col1.button("❌ Cancel"):
#         st.rerun()

#     if col2.button("🗑️ Yes, delete my account", disabled=not confirm):
#         delete(f"/users/{user_id}")
#         logout()


# ---------- DELETE CONFIRMATION DIALOG ----------
@st.dialog("Delete account")
def confirm_delete_account(user_id):
    st.error("🛑 This will permanently delete your account.")
    st.warning("This action cannot be undone.")

    password = st.text_input(
        "Confirm your password",
        type="password",
    )

    confirm = st.checkbox("I understand this action is irreversible")

    col1, col2 = st.columns(2)

    if col1.button("❌ Cancel"):
        st.rerun()

    if col2.button(
        "🗑️ Yes, delete my account",
        disabled=not (confirm and password),
    ):
        response = delete(f"/users/{user_id}", {"password": password})
        if response.status_code == 204:
            st.success("Account Deleted")
            time.sleep(5)
            logout()
        else:
            st.error("Incorrect password")


# ---------- ACTION BUTTONS ----------
if st.button("✏️ Update Profile"):
    st.session_state["edit_user"] = user

if st.button("🛑 Delete Account"):
    confirm_delete_account(user["id"])

# ---------- UPDATE FORM ----------
if "edit_user" in st.session_state:
    u = st.session_state["edit_user"]

    st.divider()
    st.subheader("Edit profile")

    with st.form("update_user"):
        first = st.text_input("First Name", u["first_name"])
        last = st.text_input("Last Name", u["last_name"])
        email = st.text_input("Email", u["email"], disabled=True)
        password = st.text_input("New Password", type="password")

        col1, col2 = st.columns(2)
        save = col1.form_submit_button("💾 Save")
        cancel = col2.form_submit_button("❌ Cancel")

    if cancel:
        del st.session_state["edit_user"]
        st.rerun()

    if save:
        if not all([first, last, password]):
            st.error("All fields required")
        else:
            put(
                f"/users/{u['id']}",
                {
                    "first_name": first,
                    "last_name": last,
                    "email": email,
                    "password": password,
                },
            )
            st.success("Profile updated — please login again")
            time.sleep(2)
            logout()
