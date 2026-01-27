import streamlit as st
from core.auth import require_auth
from core.api import post
from ui.sidebar import render_sidebar

require_auth()
render_sidebar()

st.title("➕ Create Post")

with st.form("create_post"):
    title = st.text_input("Title")
    content = st.text_area("Content")
    published = st.checkbox("Publish now?")
    submitted = st.form_submit_button("Create")

if submitted:
    if not title or not content:
        st.error("Title and content required")
    else:
        post("/posts", {
            "title": title,
            "content": content,
            "published": published
        })
        st.success("Post created 🎉")