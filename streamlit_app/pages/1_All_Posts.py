import streamlit as st
from core.auth import require_auth
from core.api import get, post
from ui.sidebar import render_sidebar

require_auth()
render_sidebar()

st.title("Feed")
st.divider()


def vote(post_id: int, direction: int):
    """
    direction:
      1 = vote
      0 = remove vote
    """
    try:
        post("/vote", {"post_id": post_id, "dir": direction})
        st.rerun()
    except Exception as e:
        st.error(f"Vote failed: {str(e)}")


posts = get("/posts")

if not posts:
    st.info("No posts available.")
    button=st.button("➕ Create Post")
    if button:
        st.switch_page("pages/3_Create_Post.py")
    st.stop()

for idx, item in enumerate(posts):
    post1 = item["Post"]
    votes = item["votes"]
    user_voted = item["user_voted"]

    post_id = post1.get("id")
    if post_id is None:
        st.error("Post ID missing.")
        continue

    st.subheader(post1["title"])
    st.write(post1["content"])
    st.caption(f"{post1['owner']['first_name']} {post1['owner']['last_name']}")

    # Button label and color based on vote status
    if user_voted:
        button_label = "Remove Vote"
        button_color = "#ff4b4b"  # red
        direction = 0
    else:
        button_label = "Vote"
        button_color = "#00c853"  # green
        direction = 1

    key = f"vote_{post_id}_{idx}"

    # CSS targeting the Streamlit button by key
    st.markdown(
        f"""
        <style>
        button[data-testid="stButton"][data-key="{key}"] {{
            background-color: {button_color} !important;
            color: white !important;
            border: none !important;
        }}
        button[data-testid="stButton"][data-key="{key}"]:hover {{
            background-color: {button_color} !important;
            opacity: 0.9 !important;
        }}
        </style>
        """,
        unsafe_allow_html=True,
    )

    # Render the button
    if st.button(button_label, key=key):
        vote(post_id, direction)

    st.markdown(f"**Votes:** {votes}")
    st.divider()
