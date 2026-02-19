import streamlit as st
from core.auth import require_auth
from core.api import get, post, patch, delete
from ui.sidebar import render_sidebar

# -------------------- AUTH --------------------
require_auth()
current_user = get("/users/profile/me")
current_user_id = current_user["id"]


# -------------------- SHARED CREATE LOGIC --------------------
def handle_create_post(title, content, published):
    if not title or not content:
        return "Title and content are required"

    try:
        post(
            "/posts",
            {"title": title, "content": content, "published": published},
        )
    except Exception as e:
        return f"Failed to create post: {str(e)}"

    return None  # success


# -------------------- SIDEBAR CREATE POST --------------------
with st.sidebar.expander("➕ Quick Post", expanded=False):
    with st.form("sidebar_create_form", clear_on_submit=True):
        sidebar_title = st.text_input("Title")
        sidebar_content = st.text_area("Content")
        sidebar_published = st.checkbox("Publish now?")

        submitted_sidebar = st.form_submit_button("Create")

    if submitted_sidebar:
        error = handle_create_post(
            sidebar_title,
            sidebar_content,
            sidebar_published,
        )

        if error:
            st.error(error)
        else:
            st.toast("Post created 🎉")
            st.rerun()

render_sidebar()


st.title("📰 Feed")
st.divider()


# -------------------- CREATE POST DIALOG --------------------
@st.dialog("➕ Create Post")
def create_post_dialog():
    with st.form("create_post_form", clear_on_submit=True):
        create_title = st.text_input("Title")
        create_content = st.text_area("Content")
        create_published = st.checkbox("Publish now?")
        col1, col2 = st.columns(2)
        cancel = col2.form_submit_button("Cancel")
        if cancel:
            st.rerun()
        submitted = col1.form_submit_button("Create")

    if submitted:
        error = handle_create_post(
            create_title,
            create_content,
            create_published,
        )

        if error:
            st.error(error)
        else:
            st.toast("Post created 🎉")
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
    with st.container(border=True):
        # --- HEADER ROW (Title + Likes on Right) ---
        header_col1, header_col2 = st.columns([5, 1])

        with header_col1:
            st.subheader(post_data["title"])
        if votes > 0:
            with header_col2:
                st.markdown(
                    f"""
                    <div style="text-align: right; font-weight: bold; font-size: 16px;">
                        👍 {votes}
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

        # --- CONTENT ---
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
                if not user_voted:
                    vote_button_text = f"👍 {vote_label}"
                else:
                    vote_button_text = f"👎🏻 {vote_label}"

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
            if not user_voted:
                vote_button_text = f"👍 {vote_label}"
            else:
                vote_button_text = f"👎🏻 {vote_label}"
            if col1.button(vote_button_text, key=vote_key, use_container_width=True):
                post("/vote", {"post_id": post_id, "dir": direction})
                st.rerun()

    st.markdown("<br>", unsafe_allow_html=True)

# -------------------- REFRESH FEED AFTER CREATE --------------------
if st.session_state.get("refresh_feed"):
    st.session_state.refresh_feed = False
    st.rerun()
