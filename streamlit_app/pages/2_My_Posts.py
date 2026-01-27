import streamlit as st
from core.auth import require_auth
from core.api import get, put, delete
from ui.sidebar import render_sidebar

require_auth()
render_sidebar()

st.title("My Posts")
st.divider()

posts = get("/posts/me")

for post in posts:
    p = post["Post"]
    post_id = p["id"]

    st.subheader(p["title"])
    st.write(p["content"])

    col1, col2 = st.columns(2)

    if col1.button("✏️ Update", key=f"upd_{post_id}"):
        st.session_state["edit_post"] = p

    if col2.button("🗑️ Delete", key=f"del_{post_id}"):
        delete(f"/posts/{post_id}")
        st.success("Post deleted")
        st.rerun()

if "edit_post" in st.session_state:
    post = st.session_state["edit_post"]

    with st.form("update_post"):
        title = st.text_input("Title", post["title"])
        content = st.text_area("Content", post["content"])
        published = st.checkbox("Published", post["published"])
        save = st.form_submit_button("Save")
        cancel = st.form_submit_button("Cancel")

    if cancel:
        del st.session_state["edit_post"]
        st.rerun()

    if save:
        put(f"/posts/{post['id']}", {
            "title": title,
            "content": content,
            "published": published
        })
        st.success("Post updated")
        del st.session_state["edit_post"]
        st.rerun()