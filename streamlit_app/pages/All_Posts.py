import requests
import streamlit as st

if not st.session_state.get("authenticated"):
    st.switch_page("app.py")

api_url = "http://127.0.0.1:8000"


def fetch_data(endpoint: str):
    token = st.session_state.get("access_token")

    if not token:
        st.error("Please login to your account to view the Posts")
        if st.button("Login"):
            st.switch_page("app.py")
        st.stop()

    headers = {"Authorization": f"Bearer {token}"}

    response = requests.get(f"{api_url}{endpoint}", headers=headers)

    if response.status_code == 401:
        st.error("Session expired. Please login again.")
        st.session_state.clear()
        st.stop()

    response.raise_for_status()
    return response.json()


st.title("Feed")
st.divider()
post_data = fetch_data("/posts")
for post in post_data:
    st.subheader(f"{post['Post']['title']}")
    st.text(f"{post['Post']['content']}")
    st.caption(
        f"{post['Post']['owner']['first_name']} {post['Post']['owner']['last_name']}"
    )

# st.sidebar.divider()

if st.sidebar.button(" ➕ Create Post"):
    st.switch_page("pages/Create_Post.py")
    

if st.sidebar.button("🚪 Sign out"):
    st.session_state.clear()
    st.switch_page("app.py")
# elif st.sidebar.button("User Profile"):
#     st.switch_page("pages/User_Profile.py")
st.divider()
if st.button("➕ Create Post"):
    st.switch_page("pages/Create_Post.py")
