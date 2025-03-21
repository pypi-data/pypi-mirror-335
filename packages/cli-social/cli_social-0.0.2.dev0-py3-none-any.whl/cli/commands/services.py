import click
import requests

API_URL = "http://localhost:8080"

@click.group()
def services():
    """Manage API services."""
    pass

@click.command()
def list_services():
    """List all available API services."""
    response = requests.get(f"{API_URL}/services")
    
    if response.status_code == 200:
        click.echo(response.json())
    else:
        click.echo(f"❌ Error retrieving services: {response.text}")

services.add_command(list_services)
