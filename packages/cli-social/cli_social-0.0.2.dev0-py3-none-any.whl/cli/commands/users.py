import click
import requests

#API_URL = "http://localhost:8080"
API_URL = "https://api.minakilabs.dev/api"

@click.group()
def users():
    """Manage users in the system."""
    pass

@click.command()
@click.argument("user_id")
def get(user_id):
    """Fetch user details."""
    response = requests.get(f"{API_URL}/users/{user_id}")
    
    if response.status_code == 200:
        click.echo(response.json())
    else:
        click.echo(f"❌ Error fetching user: {response.text}")

users.add_command(get)
