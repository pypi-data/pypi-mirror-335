import click
import requests
import os
import json

# ✅ Load API key
CONFIG_FILE = os.path.expanduser("~/.cli-social-config")

def load_api_key():
    """Load the API key from the config file."""
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, "r") as f:
            config = json.load(f)
            return config.get("api_key")
    return None

# ✅ API Base URL (Using Kong Gateway)
# API_URL = "http://localhost:8000/api/social"
API_URL = "https://api.minakilabs.dev/api/social"

@click.group()
def social():
    """Manage social interactions (posts, likes, follows)."""
    pass

# ✅ Create a Post
@click.command()
@click.argument("content")
def post(content):
    """Create a new post."""
    api_key = load_api_key()
    if not api_key:
        click.echo("❌ Not logged in. Please login first.")
        return

    response = requests.post(
        f"{API_URL}/post",
        headers={"apikey": api_key},
        json={"content": content},
    )

    if response.status_code == 200:
        click.echo("✅ Post created successfully!")
    else:
        click.echo(f"❌ Error creating post: {response.text}")

# ✅ Like a Post
@click.command()
@click.argument("post_id", type=int)
def like(post_id):
    """Like a post by post ID."""
    api_key = load_api_key()
    if not api_key:
        click.echo("❌ Not logged in. Please login first.")
        return

    response = requests.post(
        f"{API_URL}/like",
        headers={"apikey": api_key},
        json={"post_id": post_id},
    )

    if response.status_code == 200:
        click.echo("✅ Post liked successfully!")
    else:
        click.echo(f"❌ Error liking post: {response.text}")

@click.command()
@click.argument("username")
def follow(username):
    """Follow another user by their username."""
    api_key = load_api_key()
    if not api_key:
        click.echo("❌ Not logged in. Please login first.")
        return

    click.echo(f"🔹 API Key: {api_key[:6]}... (hidden for security)")
    click.echo(f"🔹 Attempting to follow user: {username}")

    # ✅ Step 1: Get the User ID
    lookup_url = f"{API_URL}/user/{username}"
    click.echo(f"🛠️ Debug: Checking user ID at {lookup_url}")

    user_lookup_response = requests.get(lookup_url, headers={"apikey": api_key})

    click.echo(f"🛠️ Debug: API Response Code: {user_lookup_response.status_code}")
    click.echo(f"🛠️ Debug: API Raw Response: {user_lookup_response.text}")

    if user_lookup_response.status_code != 200:
        click.echo(f"❌ User '{username}' does not exist.")
        return

    user_data = user_lookup_response.json()
    user_id_to_follow = user_data.get("user_id")

    if not user_id_to_follow:
        click.echo("❌ Failed to retrieve user ID from API response.")
        return

    click.echo(f"🔹 Resolved '{username}' to user_id: {user_id_to_follow}")

    # ✅ Step 2: Send Follow Request (FIXED PAYLOAD)
    follow_url = f"{API_URL}/follow"
    click.echo(f"🛠️ Debug: Sending follow request to {follow_url}")

    response = requests.post(
        follow_url,
        headers={"apikey": api_key, "Content-Type": "application/json"},
        json={"follow_username": username}  # 🔥 FIXED PAYLOAD! API expects "follow_username"
    )

    click.echo(f"🛠️ Debug: Follow API Response Code: {response.status_code}")
    click.echo(f"🛠️ Debug: Follow API Raw Response: {response.text}")

    if response.status_code == 200:
        click.echo(f"✅ Successfully followed {username}!")
    else:
        click.echo(f"❌ Error following user: {response.text}")

@click.command()
def feed():
    """Show latest posts from followed users."""
    api_key = load_api_key()
    if not api_key:
        click.echo("❌ Not logged in. Please login first.")
        return

    response = requests.get(
        f"{API_URL}/feed",
        headers={"apikey": api_key}
    )

    if response.status_code == 200:
        posts = response.json()
        click.echo("\n📢 Latest Posts:\n")
        for post in posts:
            click.echo(f"📝 [{post['post_id']}] {post['username']} - {post['content']} (❤️ {post['likes']} Likes) (Posted at {post['timestamp']})")
    else:
        click.echo(f"❌ Error fetching feed: {response.text}")


# ✅ **Comment on a Post**
@click.command()
@click.argument("post_id", type=int)
@click.argument("content")
def comment(post_id, content):
    """Add a comment to a post."""
    api_key = load_api_key()
    if not api_key:
        click.echo("❌ Not logged in. Please login first.")
        return

    response = requests.post(
        f"{API_URL}/post/comment",
        headers={"apikey": api_key, "Content-Type": "application/json"},
        json={"post_id": post_id, "content": content},
    )

    if response.status_code == 200:
        click.echo(f"✅ Comment added to post {post_id}.")
    else:
        click.echo(f"❌ Error adding comment: {response.text}")

# ✅ **Get Comments for a Post**
@click.command()
@click.argument("post_id", type=int)
def get_comments(post_id):
    """Fetch comments for a specific post."""
    api_key = load_api_key()
    if not api_key:
        click.echo("❌ Not logged in. Please login first.")
        return

    response = requests.get(
        f"{API_URL}/post/comments/{post_id}",
        headers={"apikey": api_key},
    )

    if response.status_code == 200:
        comments = response.json()
        if not comments:
            click.echo(f"📭 No comments found for post {post_id}.")
        else:
            click.echo(f"\n📨 Comments for post {post_id}:\n")
            for comment in comments:
                click.echo(f"📝 {comment['user_id']} said: {comment['content']} (📅 {comment['timestamp']})\n")
    else:
        click.echo(f"❌ Error fetching comments: {response.text}")

# ✅ **Delete a Comment**
@click.command()
@click.argument("comment_id", type=int)
def delete_comment(comment_id):
    """Delete a comment by comment ID."""
    api_key = load_api_key()
    if not api_key:
        click.echo("❌ Not logged in. Please login first.")
        return

    response = requests.delete(
        f"{API_URL}/post/comment/{comment_id}",
        headers={"apikey": api_key},
    )

    if response.status_code == 200:
        click.echo(f"✅ Comment {comment_id} deleted successfully.")
    else:
        click.echo(f"❌ Error deleting comment: {response.text}")


# ✅ Add commands to the social CLI group
social.add_command(post)
social.add_command(like)
social.add_command(follow)
social.add_command(feed)
social.add_command(comment, "add-comment")
social.add_command(get_comments, "get-comments")
social.add_command(delete_comment, "delete-comment")
