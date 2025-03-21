import click
import requests

API_URL = "http://localhost:8080"

@click.group()
def test():
    """Test API endpoints."""
    pass

@click.command()
def health():
    """Check API health."""
    response = requests.get(f"{API_URL}/api")
    
    if response.status_code == 200:
        click.echo("✅ API is running!")
    else:
        click.echo("❌ API is down!")

test.add_command(health)
