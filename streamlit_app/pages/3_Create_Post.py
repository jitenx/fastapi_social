import streamlit as st
from core.auth import require_auth
from core.api import post
from ui.sidebar import render_sidebar

require_auth()
render_sidebar()

st.title("➕ Create Post")

if "success" not in st.session_state:
    st.session_state.success = False

if "error" not in st.session_state:
    st.session_state.error = None


def submit_post():
    if not st.session_state.title or not st.session_state.content:
        st.session_state.error = "Title and content required"
        return

    post("/posts", {
        "title": st.session_state.title,
        "content": st.session_state.content,
        "published": st.session_state.published
    })

    # clear form
    st.session_state.title = ""
    st.session_state.content = ""
    st.session_state.published = False
    st.session_state.success = True
    st.session_state.error = None


with st.form("create_post"):
    st.text_input("Title", key="title")
    st.text_area("Content", key="content")
    st.checkbox("Publish now?", key="published")
    st.form_submit_button("Create", on_click=submit_post)

if st.session_state.get("error"):
    st.error(st.session_state.error)

if st.session_state.get("success"):
    st.success("Post created 🎉")
    st.session_state.success = False
