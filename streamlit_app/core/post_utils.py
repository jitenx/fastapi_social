# core/post_utils.py

from datetime import datetime
from core.api import get, post, patch, delete


# -------------------- TIME AGO --------------------
def time_ago(timestamp_str):
    """
    Convert ISO 8601 timestamp string to human-friendly 'X second(s)/minute(s)/hour(s)/day(s)/year(s) ago'.
    Supports:
      - 'YYYY-MM-DDTHH:MM:SS'
      - 'YYYY-MM-DDTHH:MM:SS.microseconds'
    """
    now = datetime.now()
    dt = None

    for fmt in ("%Y-%m-%dT%H:%M:%S.%f", "%Y-%m-%dT%H:%M:%S"):
        try:
            dt = datetime.strptime(timestamp_str, fmt)
            break
        except ValueError:
            continue

    if dt is None:
        return timestamp_str  # fallback

    diff = now - dt
    seconds = int(diff.total_seconds())

    if seconds < 60:
        return f"{seconds} second{'s' if seconds != 1 else ''} ago"
    minutes = seconds // 60
    if minutes < 60:
        return f"{minutes} minute{'s' if minutes != 1 else ''} ago"
    hours = minutes // 60
    if hours < 24:
        return f"{hours} hour{'s' if hours != 1 else ''} ago"
    days = hours // 24
    if days < 365:
        return f"{days} day{'s' if days != 1 else ''} ago"
    years = days // 365
    return f"{years} year{'s' if years != 1 else ''} ago"


# -------------------- POST HANDLERS --------------------
def handle_create_post(title, content, published):
    if not title or not content:
        return "Title and content are required"
    try:
        post("/posts", {"title": title, "content": content, "published": published})
    except Exception as e:
        return f"Failed to create post: {str(e)}"
    return None  # success


def fetch_posts_batch(batch_size, post_skip):
    new_posts = get(f"/posts?limit={batch_size}&skip={post_skip}")
    return new_posts


def update_post(post_id, title, content, published):
    patch(
        f"/posts/{post_id}",
        {"title": title, "content": content, "published": published},
    )


def delete_post(post_id):
    delete(f"/posts/{post_id}")


def vote_post(post_id, direction):
    post("/vote", {"post_id": post_id, "dir": direction})
