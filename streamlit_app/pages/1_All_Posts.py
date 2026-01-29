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

    col1, col2, col3 = st.columns([1, 1, 8])

    with col1:
        # Upvote button enabled only if user has NOT voted
        if st.button("⬆", key=f"up_{post_id}_{idx}", disabled=user_voted):
            vote(post_id, 1)

    with col2:
        st.markdown(f"**{votes}**")

    with col3:
        # Downvote button enabled only if user HAS voted
        if st.button("⬇", key=f"down_{post_id}_{idx}", disabled=not user_voted):
            vote(post_id, 0)

    st.divider()
