import requests
import streamlit as st

if not st.session_state.get("authenticated"):
    st.switch_page("app.py")

API_BASE = "http://127.0.0.1:8000"


def get_token():
    token = st.session_state.get("access_token")
    if not token:
        st.error("Please login to view posts")
        if st.button("Login"):
            st.switch_page("app.py")
        st.stop()
    return {"Authorization": f"Bearer {token}"}


def fetch_data(endpoint: str):
    headers = get_token()
    response = requests.get(f"{API_BASE}{endpoint}", headers=headers)
    if response.status_code == 401:
        st.error("Session expired. Please login again.")
        st.session_state.clear()
        st.stop()
    response.raise_for_status()
    return response.json()


st.title("Dashboard")

post_data = fetch_data("/posts/me")

# Show list of posts
for post in post_data:
    post_id = post["Post"]["id"]

    st.subheader(post["Post"]["title"])
    st.write(post["Post"]["content"])

    col1, col2 = st.columns(2)

    with col1:
        if st.button("Update", key=f"update_{post_id}"):
            st.session_state["edit_post_id"] = post_id
            st.session_state["edit_post_data"] = post["Post"]
            st.rerun()

    with col2:
        if st.button("Delete", key=f"delete_{post_id}"):
            headers = get_token()
            response = requests.delete(f"{API_BASE}/posts/{post_id}", headers=headers)
            if response.status_code == 204:
                st.success("Post deleted")
                st.rerun()

# ---------- UPDATE FORM ----------
if st.session_state.get("edit_post_id"):
    post_id = st.session_state["edit_post_id"]
    post = st.session_state["edit_post_data"]

    st.markdown("---")
    st.title("Update Post")

    with st.form("update_form", clear_on_submit=False):
        title = st.text_input("Title", value=post["title"], key="title_upd")
        content = st.text_area("Content", value=post["content"], key="content_upd")
        published = st.checkbox(
            "Published?", value=post["published"], key="published_upd"
        )

        update_btn = st.form_submit_button("Update", key="submit_update")
        cancel_btn = st.form_submit_button("Cancel", key="cancel_update")

    if cancel_btn:
        del st.session_state["edit_post_id"]
        del st.session_state["edit_post_data"]
        st.rerun()

    if update_btn:
        if not title:
            st.error("Title field cannot be blank")
        elif not content:
            st.error("Content field cannot be blank")
        else:
            payload = {"title": title, "content": content, "published": published}
            headers = get_token()
            response = requests.put(
                f"{API_BASE}/posts/{post_id}", json=payload, headers=headers
            )

            if response.status_code == 200:
                st.success("Post updated successfully!")
                del st.session_state["edit_post_id"]
                del st.session_state["edit_post_data"]
                st.rerun()
            else:
                st.error("Failed to update post")
                st.write(response.text)


# Sidebar logout
st.sidebar.divider()
if st.sidebar.button("🚪 Sign out"):
    st.session_state.clear()
    st.switch_page("app.py")

st.divider()
if st.button("Create another Post"):
    st.switch_page("pages/Create_Post.py")
