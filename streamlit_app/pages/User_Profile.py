# streamlit_app.py
import streamlit as st
import requests
import time

if not st.session_state.get("authenticated"):
    st.switch_page("app.py")

st.title("Personal Profile")
# The API URL
api_url = "http://127.0.0.1:8000"

def get_token():
    token = st.session_state.get("access_token")
    if not token:
        st.error("Please login to view your user data")
        if st.button("Login"):
            st.switch_page("app.py")
        st.stop()
    return {"Authorization": f"Bearer {token}"}

def fetch_data(endpoint: str):
    headers = get_token()
    response = requests.get(f"{api_url}{endpoint}", headers=headers)
    if response.status_code == 401:
        st.error("Session expired. Please login again.")
        st.session_state.clear()
        st.stop()
    response.raise_for_status()
    return response.json()



st.divider()
user_data = fetch_data("/users/profile/me")
st.info(f"""
Name: {user_data["first_name"]} {user_data["last_name"]}\n
Email: {user_data["email"]}
""")
user_id=user_data["id"]

col1, col2 = st.columns(2)

with col1:
    if st.button("Update", key=f"update_{user_id}"):
        st.session_state["edit_user_id"] = user_id
        st.session_state["edit_user_data"] = user_data
        st.rerun()

with col2:
    confirm = st.checkbox("I understand and want to delete")
    st.warning("⚠️ This action is irreversible")
    if st.button("Delete",key=f"delete_{user_id}",disabled=not confirm) and confirm:
        st.success("Deleted")
    # if st.button("Delete", key=f"delete_{user_id}"):
        headers = get_token()
        response = requests.delete(f"{api_url}/users/{user_id}", headers=headers)
        if response.status_code == 204:
            st.success("User deleted")
            st.session_state.clear()
            st.switch_page("app.py")


if st.session_state.get("edit_user_id"):
    post_id = st.session_state["edit_user_id"]
    post = st.session_state["edit_user_data"]

    st.markdown("---")
    st.title("Update User")

    with st.form("update_form", clear_on_submit=False):
        first_name = st.text_input("First Name", value=user_data["first_name"], key="first_name")
        last_name = st.text_input("Last Name", value=user_data["last_name"], key="last_name")
        email = st.text_input("Email", value=user_data["email"], key="email",disabled=True)
        password = st.text_input("Password", value=None, key="password")
        update_btn = st.form_submit_button("Update", key="submit_update")
        cancel_btn = st.form_submit_button("Cancel", key="cancel_update")

    if cancel_btn:
        del st.session_state["edit_user_id"]
        del st.session_state["edit_user_data"]
        st.rerun()

    if update_btn:
        if not first_name:
            st.error("First Name cannot be blank")
        elif not last_name:
            st.error("Last Name cannot be blank")
        else:
            payload = {"first_name": first_name, "last_name": last_name,"email":email,"password":password}
            headers = get_token()
            response = requests.put(
                f"{api_url}/users/{user_id}", json=payload, headers=headers
            )

            if response.status_code == 200:
                st.success("User updated successfully!")
                st.info("You will be logged out now for re-login")
                del st.session_state["edit_user_id"]
                del st.session_state["edit_user_data"]
                # st.rerun()
                with st.spinner("Please wait..."):
                        time.sleep(2)
                st.session_state.clear()
                st.switch_page("app.py")
            else:
                st.error("Failed to update user")
                st.write(response.text)


# Sidebar logout
# st.sidebar.divider()
if st.sidebar.button("🚪 Sign out"):
    st.session_state.clear()
    st.switch_page("app.py")
