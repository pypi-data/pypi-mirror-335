import click
import requests
from cli.utils import load_api_key  # ✅ Now importing from the new utils.py

#API_URL = "http://localhost:8000/api/social"

API_URL = "https://api.minakilabs.dev/api/social"

@click.group()
def unsocial():
    """Commands for unfollowing, unliking, and deleting posts."""
    pass

@click.command()
@click.argument("username")
def unfollow(username):
    """Unfollow a user by username."""
    api_key = load_api_key()
    if not api_key:
        click.echo("❌ Not logged in. Please login first.")
        return

    response = requests.post(
        f"{API_URL}/unfollow",
        headers={"apikey": api_key, "Content-Type": "application/json"},
        json={"unfollow_username": username},
    )

    if response.status_code == 200:
        click.echo(f"✅ Successfully unfollowed {username}!")
    else:
        click.echo(f"❌ Error unfollowing user: {response.text}")

@click.command()
@click.argument("post_id", type=int)
def unlike(post_id):
    """Unlike a post by post ID."""
    api_key = load_api_key()
    if not api_key:
        click.echo("❌ Not logged in. Please login first.")
        return

    response = requests.post(
        f"{API_URL}/unlike",
        headers={"apikey": api_key, "Content-Type": "application/json"},
        json={"post_id": post_id},
    )

    if response.status_code == 200:
        click.echo(f"✅ Successfully unliked post {post_id}!")
    else:
        click.echo(f"❌ Error unliking post: {response.text}")

@click.command()
@click.argument("post_id", type=int)
def delete_post(post_id):
    """Delete a post by post ID."""
    api_key = load_api_key()
    if not api_key:
        click.echo("❌ Not logged in. Please login first.")
        return

    response = requests.post(
        f"{API_URL}/delete_post",
        headers={"apikey": api_key, "Content-Type": "application/json"},
        json={"post_id": post_id},
    )

    if response.status_code == 200:
        click.echo(f"✅ Successfully deleted post {post_id}!")
    else:
        click.echo(f"❌ Error deleting post: {response.text}")

unsocial.add_command(unfollow)
unsocial.add_command(unlike)
unsocial.add_command(delete_post)
