import streamlit as st
from core.auth import require_auth
from core.api import get, put, delete
from ui.sidebar import render_sidebar

require_auth()
render_sidebar()

st.title("My Posts")
st.divider()

posts = get("/posts/me")
if not posts:
    st.info("You have not posted anything yet.")
    button=st.button("➕ Create Post")
    if button:
        st.switch_page("pages/3_Create_Post.py")
    st.stop()


# ---------- DELETE CONFIRMATION DIALOG ----------
@st.dialog("Confirm delete")
def confirm_delete(post_id):
    st.warning(
        "⚠️ Are you sure you want to delete this post? This action cannot be undone."
    )

    col1, col2 = st.columns(2)

    if col1.button("❌ Cancel"):
        st.rerun()

    if col2.button("🗑️ Yes, delete"):
        delete(f"/posts/{post_id}")
        st.success("Post deleted")
        st.rerun()


# ---------- POSTS LIST ----------
for post in posts:
    p = post["Post"]
    post_id = p["id"]

    st.subheader(p["title"])
    st.write(p["content"])

    col1, col2 = st.columns(2)

    if col1.button("✏️ Update", key=f"upd_{post_id}"):
        st.session_state["edit_post"] = p

    if col2.button("🗑️ Delete", key=f"del_{post_id}"):
        confirm_delete(post_id)

# ---------- UPDATE FORM ----------
if "edit_post" in st.session_state:
    post = st.session_state["edit_post"]

    st.divider()
    st.subheader("Edit post")

    with st.form("update_post"):
        title = st.text_input("Title", post["title"])
        content = st.text_area("Content", post["content"])
        published = st.checkbox("Published", post["published"])

        col1, col2 = st.columns(2)
        save = col1.form_submit_button("💾 Save")
        cancel = col2.form_submit_button("❌ Cancel")

    if cancel:
        del st.session_state["edit_post"]
        st.rerun()

    if save:
        put(
            f"/posts/{post['id']}",
            {
                "title": title,
                "content": content,
                "published": published,
            },
        )
        st.success("Post updated")
        del st.session_state["edit_post"]
        st.rerun()
