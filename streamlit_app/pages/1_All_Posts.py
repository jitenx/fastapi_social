import streamlit as st
from core.auth import require_auth
from core.api import get, post, patch, delete
from ui.sidebar import render_sidebar


st.markdown(
    """
<style>

/* Base vote button */
button[data-testid="stButton"] {
    border-radius: 999px !important;
    font-weight: 500 !important;
    transition: all 0.2s ease-in-out !important;
}

/* Hover animation */
button[data-testid="stButton"]:hover {
    transform: translateY(-1px);
    box-shadow: 0 6px 14px rgba(0,0,0,0.08);
}

/* Upvote style */
.vote-up button {
    background-color: #EEF2FF !important;
    color: #3730A3 !important;
    border: 1px solid #C7D2FE !important;
}

/* Downvote style (when user voted) */
.vote-down button {
    background-color: #FEE2E2 !important;
    color: #991B1B !important;
    border: 1px solid #FCA5A5 !important;
}

</style>
""",
    unsafe_allow_html=True,
)


# -------------------- AUTH --------------------
require_auth()
current_user = get("/users/profile/me")
current_user_id = current_user["id"]

render_sidebar()

st.title("📰 Feed")
st.divider()


# -------------------- CREATE POST DIALOG --------------------
@st.dialog("➕ Create Post")
def create_post_dialog():
    # Initialize session_state
    for key in [
        "create_error",
        "create_title",
        "create_content",
        "create_published",
        "refresh_feed",
    ]:
        if key not in st.session_state:
            st.session_state[key] = "" if "title" in key or "content" in key else False

    # Callback to handle post creation
    def submit_post():
        title = st.session_state.create_title
        content = st.session_state.create_content
        published = st.session_state.create_published

        # Validation
        if not title or not content:
            st.session_state.create_error = "Title and content are required"
            return

        try:
            post(
                "/posts",
                {"title": title, "content": content, "published": published},
            )
        except Exception as e:
            st.session_state.create_error = f"Failed to create post: {str(e)}"
            return

        # Success → set flags to reset form after render
        st.session_state.create_error = None
        st.session_state.create_title = ""
        st.session_state.create_content = ""
        st.session_state.create_published = False
        st.session_state.refresh_feed = True
        st.session_state._rerun_needed = True  # custom flag

    # -------------------- FORM --------------------
    with st.form("create_post_form"):
        st.text_input("Title", key="create_title")
        st.text_area("Content", key="create_content")
        st.checkbox("Publish now?", key="create_published")

        col1, col2 = st.columns(2)
        col1.form_submit_button("Create", on_click=submit_post)
        cancel = col2.form_submit_button("Cancel")
        if cancel:
            st.rerun()

    # -------------------- SHOW ERROR --------------------
    if st.session_state.create_error:
        st.error(st.session_state.create_error)

    # -------------------- RERUN IF NEEDED --------------------
    # This runs outside the callback
    if "_rerun_needed" in st.session_state and st.session_state._rerun_needed:
        st.session_state._rerun_needed = False
        st.rerun()


# -------------------- UPDATE POST DIALOG --------------------
@st.dialog("✏️ Update Post")
def update_post_dialog(post_data):
    if post_data["owner_id"] != current_user_id:
        st.error("You are not allowed to edit this post.")
        return

    with st.form("update_post_form"):
        title = st.text_input("Title", post_data["title"])
        content = st.text_area("Content", post_data["content"])
        published = st.checkbox("Published", post_data["published"])

        col1, col2 = st.columns(2)
        save = col1.form_submit_button("💾 Save")
        cancel = col2.form_submit_button("Cancel")
        if cancel:
            st.rerun()

    if save:
        with st.spinner("Updating post..."):
            patch(
                f"/posts/{post_data['id']}",
                {
                    "title": title,
                    "content": content,
                    "published": published,
                },
            )
        st.toast("Post updated successfully ✅")
        # Refresh feed after update
        st.rerun()


# -------------------- DELETE POST DIALOG --------------------
@st.dialog("🗑️ Confirm Delete")
def confirm_delete(post_id):
    st.warning("This action cannot be undone.")
    col1, col2 = st.columns(2)
    if col2.button("Cancel"):
        st.rerun()
    if col1.button("Delete", type="primary"):
        delete(f"/posts/{post_id}")
        st.toast("Post deleted 🗑️")
        st.rerun()


# -------------------- LOAD POSTS --------------------
posts = get("/posts")

# Button to open Create Post dialog
st.button("➕ Create Post", on_click=create_post_dialog)

if not posts:
    st.info("No posts available.")
    st.stop()


# -------------------- DISPLAY POSTS --------------------
for idx, item in enumerate(posts):
    post_data = item["Post"]
    votes = item["votes"]
    user_voted = item["user_voted"]

    post_id = post_data.get("id")
    if post_id is None:
        continue

    is_owner = post_data["owner_id"] == current_user_id
    is_published = post_data["published"]

    vote_key = f"vote_{post_id}_{idx}"
    expand_key = f"expand_{post_id}"

    # Vote state
    if user_voted:
        direction = 0
        vote_label = "Downvote"
    else:
        direction = 1
        vote_label = "Vote"

    # Preview logic
    full_content = post_data["content"]
    preview_limit = 220

    if expand_key not in st.session_state:
        st.session_state[expand_key] = False

    show_full = st.session_state[expand_key]

    if not show_full and len(full_content) > preview_limit:
        display_content = full_content[:preview_limit] + "..."
        show_read_more = True
    else:
        display_content = full_content
        show_read_more = False

    # -------------------- CARD --------------------
    with st.container():
        col1, col2 = st.columns([5, 1])

    with col1:
        st.markdown(f"### {post_data['title']}")

    with col2:
        st.markdown(f"👍 **{votes}**")

    st.markdown(display_content)
    st.caption(
        f"👤 {post_data['owner']['first_name']} {post_data['owner']['last_name']}"
    )
    # -------------------- READ MORE --------------------
    if show_read_more:
        if st.button(
            "Read more",
            key=f"read_{post_id}",
            use_container_width=False,
        ):
            st.session_state[expand_key] = True
            st.rerun()

    if show_full and len(full_content) > preview_limit:
        if st.button(
            "Show less",
            key=f"less_{post_id}",
            use_container_width=False,
        ):
            st.session_state[expand_key] = False
            st.rerun()

    # -------------------- DRAFT BADGE --------------------
    if is_owner and not is_published:
        st.warning("📝 Draft — Not Published")

    # -------------------- ACTION ROW --------------------
    col1, col2, col3 = st.columns([1, 1, 1])

    vote_text = "👎" if user_voted else "👍"

    if is_owner:
        if not is_published:
            if col1.button(
                "🚀 Publish", key=f"pub_{post_id}", use_container_width=True
            ):
                with st.spinner("Publishing..."):
                    patch(
                        f"/posts/{post_id}",
                        {
                            "title": post_data["title"],
                            "content": post_data["content"],
                            "published": True,
                        },
                    )
                st.success("Post published 🚀")
                st.balloons()
                st.rerun()

        else:
            if col1.button(vote_text, key=vote_key, use_container_width=True):
                post("/vote", {"post_id": post_id, "dir": direction})
                st.rerun()

        if col2.button("✏️ Update", key=f"upd_{post_id}", use_container_width=True):
            update_post_dialog(post_data)

        if col3.button("🗑️ Delete", key=f"del_{post_id}", use_container_width=True):
            with st.spinner("Deleting..."):
                confirm_delete(post_id)
            st.toast("Post deleted")
            st.rerun()

    else:
        if col1.button(vote_text, key=vote_key, use_container_width=True):
            post("/vote", {"post_id": post_id, "dir": direction})
            st.rerun()


# -------------------- REFRESH FEED AFTER CREATE --------------------
if st.session_state.get("refresh_feed"):
    st.session_state.refresh_feed = False
    st.rerun()
