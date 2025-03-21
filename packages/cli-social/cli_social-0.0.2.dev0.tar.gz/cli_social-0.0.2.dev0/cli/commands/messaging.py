import click
import requests
import json
from cli.utils import load_api_key

#API_URL = "http://localhost:8000/api/dm"  # Corrected base API URL
API_URL = "https://api.minakilabs.dev/api/dm"

#USER_LOOKUP_URL = "http://localhost:8000/api/social/user"  # Corrected user lookup URL
USER_LOOKUP_URL = "https://api.minakilabs.dev/api/social/user"  # Corrected user lookup URL

@click.group()
def messaging():
    """Manage direct messages (DMs) securely."""
    pass

# ✅ **Helper Function: Get User ID from Username**
def get_user_id(username, api_key):
    """Retrieve user ID from username via API."""
    try:
        url = f"{USER_LOOKUP_URL}/{username}"  # Ensure the correct API path
        response = requests.get(url, headers={"apikey": api_key})
        
        print(f"DEBUG: Request URL -> {url}")  # Debugging print
        print(f"DEBUG: Response Status -> {response.status_code}")  # Debugging print
        print(f"DEBUG: Response Data -> {response.text}")  # Debugging print

        if response.status_code == 200:
            return response.json().get("user_id")
        elif response.status_code == 404:
            click.secho(f"❌ User '{username}' not found.", fg="red")
        else:
            click.secho(f"❌ API Error: {response.text}", fg="red")
    except requests.exceptions.RequestException as e:
        click.secho(f"❌ Connection error: {e}", fg="red")
    
    return None

# ✅ **Send a Direct Message**
@click.command()
@click.argument("receiver_username")
@click.argument("content")
def send(receiver_username, content):
    """Send a direct message to another user."""
    api_key = load_api_key()
    if not api_key:
        click.secho("❌ Not logged in. Please login first.", fg="red")
        return

    receiver_id = get_user_id(receiver_username, api_key)
    if not receiver_id:
        return

    try:
        response = requests.post(
            f"{API_URL}/send",
            headers={"apikey": api_key, "Content-Type": "application/json"},
            json={"receiver_id": receiver_id, "content": content},
        )

        if response.status_code == 200:
            click.secho(f"✅ Message sent to {receiver_username}!", fg="green")
        else:
            click.secho(f"❌ Error sending message: {response.text}", fg="red")

    except requests.exceptions.RequestException as e:
        click.secho(f"❌ Connection error: {e}", fg="red")

# ✅ **View Conversation with a User**
@click.command()
@click.argument("receiver_username")
def conversation(receiver_username):
    """View conversation between you and another user."""
    api_key = load_api_key()
    if not api_key:
        click.secho("❌ Not logged in. Please login first.", fg="red")
        return

    receiver_id = get_user_id(receiver_username, api_key)
    if not receiver_id:
        return

    try:
        response = requests.get(f"{API_URL}/conversation/{receiver_id}", headers={"apikey": api_key})

        if response.status_code == 200:
            messages = response.json()
            if not messages:
                click.secho(f"📭 No messages with {receiver_username}.", fg="yellow")
                return

            click.secho(f"\n📬 Conversation with {receiver_username}:\n", fg="cyan")
            for msg in messages:
                sender = "You" if msg["sender"] != receiver_id else receiver_username
                status = "✔️ Read" if msg["is_read"] else "📩 Unread"
                click.secho(f"{sender}: {msg['content']} {status}", fg="white")

        else:
            click.secho(f"❌ Error retrieving messages: {response.text}", fg="red")

    except requests.exceptions.RequestException as e:
        click.secho(f"❌ Connection error: {e}", fg="red")

# ✅ **Check Unread Messages**
@click.command()
def unread():
    """Check unread messages."""
    api_key = load_api_key()
    if not api_key:
        click.secho("❌ Not logged in. Please login first.", fg="red")
        return

    try:
        response = requests.get(f"{API_URL}/unread", headers={"apikey": api_key})

        if response.status_code == 200:
            messages = response.json()
            if not messages:
                click.secho("✅ No unread messages!", fg="green")
                return

            click.secho("\n📨 Unread Messages:\n", fg="cyan")
            for msg in messages:
                #click.secho(f"📩 {msg['sender']}: {msg['content']}", fg="white")
                click.secho(f"📩 {msg['sender']}: {msg['content']} (UUID: {msg['message_uuid']})", fg="white")

        else:
            click.secho(f"❌ Error fetching unread messages: {response.text}", fg="red")

    except requests.exceptions.RequestException as e:
        click.secho(f"❌ Connection error: {e}", fg="red")

# ✅ Mark a Message as Read
@click.command()
@click.argument("message_uuid", type=str)
def mark_read(message_uuid):
    """Mark a message as read using UUID."""
    api_key = load_api_key()
    if not api_key:
        click.secho("❌ Not logged in. Please login first.", fg="red")
        return

    try:
        response = requests.put(
            f"{API_URL}/mark-read",
            headers={"apikey": api_key, "Content-Type": "application/json"},
            json={"message_uuid": message_uuid},  # ✅ Corrected field name
        )

        if response.status_code == 200:
            click.secho(f"✅ Message {message_uuid} marked as read.", fg="green")
        else:
            click.secho(f"❌ Error marking message as read: {response.text}", fg="red")

    except requests.exceptions.RequestException as e:
        click.secho(f"❌ Connection error: {e}", fg="red")


# ✅ Delete a Message
@click.command()
@click.argument("message_uuid", type=str)
def delete(message_uuid):
    """Delete a message using UUID."""
    api_key = load_api_key()
    if not api_key:
        click.secho("❌ Not logged in. Please login first.", fg="red")
        return

    try:
        response = requests.delete(
            f"{API_URL}/delete",
            headers={"apikey": api_key, "Content-Type": "application/json"},
            json={"message_uuid": message_uuid},  # ✅ Corrected field name
        )

        if response.status_code == 200:
            click.secho(f"✅ Message {message_uuid} deleted.", fg="green")
        else:
            click.secho(f"❌ Error deleting message: {response.text}", fg="red")

    except requests.exceptions.RequestException as e:
        click.secho(f"❌ Connection error: {e}", fg="red")

# ✅ **Add Commands to Messaging Group**
messaging.add_command(send)
messaging.add_command(conversation)
messaging.add_command(unread)
messaging.add_command(mark_read)
messaging.add_command(delete)
