import requests
import streamlit as st

if not st.session_state.get("authenticated"):
    st.switch_page("app.py")

API_BASE = "http://127.0.0.1:8000"


def fetch_data(endpoint: str):
    token = st.session_state.get("access_token")

    if not token:
        st.error("Please login to your account to create Post")
        if st.button("Login"):
            st.switch_page("app.py")
        st.stop()


st.title("➕ Create Post")
form_values = {
    "title": None,
    "content": None,
    "published": None,
}

with st.form("create_item_form", clear_on_submit=True):
    form_values["title"] = st.text_input("Title", placeholder="Title")
    form_values["content"] = st.text_area(
        "Description", placeholder="Description of your Post"
    )
    form_values["published"] = st.checkbox("Publish Now?")
    submitted = st.form_submit_button("Create")
headers = {"Authorization": f"Bearer {st.session_state['access_token']}"}
if submitted:
    if not form_values["title"]:
        st.error("Please enter title of the post")
    elif not form_values["content"]:
        st.error("Please enter Description of the post")
    else:
        payload = {
            "title": form_values["title"],
            "content": form_values["content"],
            "published": form_values["published"],
        }

        with st.spinner("Sending request..."):
            response = requests.post(f"{API_BASE}/posts", json=payload, headers=headers)
            data = response.json()
        if response.status_code == 201:
            st.success("Post created successfully 🎉")
            # st.json(data)
            st.info(f"""
            Title: {data["title"]} \n
            Description: {data["content"]} \n
            Author: {data["owner"]["first_name"]} {data["owner"]["last_name"]}
            """)

            # st.switch_page("pages/Posts.py")
        else:
            st.error("Failed to create item")
            st.text(response.text)
