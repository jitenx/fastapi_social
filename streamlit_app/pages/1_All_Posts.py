import streamlit as st
from core.auth import require_auth
from core.api import get, post, patch, delete
from ui.sidebar import render_sidebar

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
    if "create_error" not in st.session_state:
        st.session_state.create_error = None

    def submit_post():
        if not st.session_state.create_title or not st.session_state.create_content:
            st.session_state.create_error = "Title and content are required"
            return

        try:
            post(
                "/posts",
                {
                    "title": st.session_state.create_title,
                    "content": st.session_state.create_content,
                    "published": st.session_state.create_published,
                },
            )
        except Exception as e:
            st.session_state.create_error = f"Failed to create post: {str(e)}"
            return

        # Clear form
        st.session_state.create_title = ""
        st.session_state.create_content = ""
        st.session_state.create_published = False
        st.session_state.create_error = None

        # Flag to refresh feed after dialog closes
        st.session_state.refresh_feed = True
        return  # close the dialog

    # -------------------- FORM --------------------
    with st.form("create_post_form"):
        st.text_input("Title", key="create_title")
        st.text_area("Content", key="create_content")
        st.checkbox("Publish now?", key="create_published")

        col1, col2 = st.columns(2)
        create = col1.form_submit_button("Create", on_click=submit_post)

        cancel = col2.form_submit_button("Cancel")
        if cancel:
            st.rerun()
        if create:
            with st.spinner("Creating post..."):
                st.toast("Post created successfully ✅")
                st.rerun()

    if st.session_state.create_error:
        st.error(st.session_state.create_error)


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

    with st.container(border=True):
        st.subheader(post_data["title"])
        st.write(post_data["content"])
        st.caption(
            f"👤 {post_data['owner']['first_name']} {post_data['owner']['last_name']}"
        )

        # Draft badge
        if is_owner and not is_published:
            st.warning("📝 Draft (Not Published)")

        # Vote state
        if user_voted:
            vote_label = "Remove Vote"
            vote_color = "#ff4b4b"
            direction = 0
        else:
            vote_label = "Vote"
            vote_color = "#00c853"
            direction = 1

        vote_key = f"vote_{post_id}_{idx}"

        # Style vote button
        st.markdown(
            f"""
            <style>
            button[data-testid="stButton"][data-key="{vote_key}"] {{
                background-color: {vote_color} !important;
                color: white !important;
                border: none !important;
            }}
            button[data-testid="stButton"][data-key="{vote_key}"]:hover {{
                background-color: {vote_color} !important;
                opacity: 0.9 !important;
            }}
            </style>
            """,
            unsafe_allow_html=True,
        )

        # -------------------- ACTION ROW --------------------
        if is_owner:
            col1, col2, col3 = st.columns([1, 1, 1])

            # Column 1: Vote or Publish
            if not is_published:
                if col1.button(
                    "🚀 Publish", key=f"pub_{post_id}", use_container_width=True
                ):
                    patch(
                        f"/posts/{post_id}",
                        {
                            "title": post_data["title"],
                            "content": post_data["content"],
                            "published": True,
                        },
                    )
                    st.toast("Post published successfully 🚀")
                    st.rerun()
            else:
                if votes != 0:
                    vote_button_text = f"👍 {votes}  {vote_label}"
                else:
                    vote_button_text = f"{vote_label}"

                if col1.button(
                    vote_button_text, key=vote_key, use_container_width=True
                ):
                    post("/vote", {"post_id": post_id, "dir": direction})
                    st.rerun()

            # Column 2: Update
            if col2.button("✏️ Update", key=f"upd_{post_id}", use_container_width=True):
                update_post_dialog(post_data)

            # Column 3: Delete
            if col3.button("🗑️ Delete", key=f"del_{post_id}", use_container_width=True):
                confirm_delete(post_id)

        else:
            # Non-owner: center vote button
            col1, col2, col3 = st.columns([1, 1, 1])
            if votes != 0:
                vote_button_text = f"👍 {votes}  {vote_label}"
            else:
                vote_button_text = f"{vote_label}"
            if col1.button(vote_button_text, key=vote_key, use_container_width=True):
                post("/vote", {"post_id": post_id, "dir": direction})
                st.rerun()

    st.markdown("<br>", unsafe_allow_html=True)

# -------------------- REFRESH FEED AFTER CREATE --------------------
if st.session_state.get("refresh_feed"):
    st.session_state.refresh_feed = False
    st.rerun()
