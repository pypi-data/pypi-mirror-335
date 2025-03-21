import click
import requests
import os
import json

# ✅ Use Kong API URL
#API_URL = "http://localhost:8000/api"
API_URL = "https://api.minakilabs.dev/api"
CONFIG_FILE = os.path.expanduser("~/.cli-social-config")

def save_login(username, api_key):
    """Save the API key and username locally in a config file."""
    config = {"username": username, "api_key": api_key}
    with open(CONFIG_FILE, "w") as f:
        json.dump(config, f)
    os.chmod(CONFIG_FILE, 0o600)  # Restrict file permissions

def load_login():
    """Load the username and API key from the config file."""
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, "r") as f:
            return json.load(f)
    return None

@click.group()
def auth():
    """Manage authentication with the API."""
    pass

@click.command()
@click.argument("username")
@click.argument("api_key")
def register(username, api_key):
    """Register a new user with a username and API key."""
    response = requests.post(f"{API_URL}/social/register", json={"username": username}, headers={"apikey": api_key})

    if response.status_code == 200:
        data = response.json()
        save_login(username, api_key)
        click.echo(f"✅ Successfully registered as {username}. API key saved.")
    else:
        click.echo(f"❌ Registration failed: {response.text}")

@click.command()
@click.argument("username")
@click.argument("api_key")
def login(username, api_key):
    """Login using username and API key, and store them locally."""
    response = requests.get(f"{API_URL}/social/login?username={username}", headers={"apikey": api_key})

    if response.status_code == 200:
        data = response.json()
        if data["username"] != username:
            click.echo(f"❌ Login failed: The provided API key does not belong to {username}.")
            return
        
        save_login(username, api_key)
        click.echo(f"✅ Successfully logged in as {username}. API key saved.")
    else:
        click.echo(f"❌ Login failed: {response.text}")

@click.command()
def logout():
    """Logout and remove stored API key and username."""
    if os.path.exists(CONFIG_FILE):
        os.remove(CONFIG_FILE)
        click.echo("✅ Logged out successfully. API key and username removed.")
    else:
        click.echo("❌ No API key found. You are not logged in.")

@click.command()
def status():
    """Check if the user is logged in."""
    login_data = load_login()
    if login_data:
        click.echo(f"✅ Logged in as {login_data['username']}. API Key: {login_data['api_key'][:4]}... (hidden for security)")
    else:
        click.echo("❌ Not logged in.")

auth.add_command(register)
auth.add_command(login)
auth.add_command(logout)
auth.add_command(status)
