import streamlit as st
from core.auth import require_auth
from core.api import get
from ui.sidebar import render_sidebar

require_auth()
render_sidebar()

st.title("Feed")
st.divider()

posts = get("/posts")

for post in posts:
    p = post["Post"]
    st.title(p["title"])
    st.write(p["content"])
    st.caption(f"{p['owner']['first_name']} {p['owner']['last_name']}")
