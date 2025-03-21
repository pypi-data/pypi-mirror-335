import click
from cli.commands import auth, users, services, test, social, unsocial, messaging

@click.group()
def cli():
    """CLI tool for interacting with the API."""
    pass

cli.add_command(auth.auth)
cli.add_command(users.users)
cli.add_command(services.services)
cli.add_command(test.test)
cli.add_command(social.social)  # ✅ Add the new social CLI group
cli.add_command(unsocial.unsocial)
cli.add_command(messaging.messaging)  # ✅ Add messaging CLI group


if __name__ == "__main__":
    cli()
