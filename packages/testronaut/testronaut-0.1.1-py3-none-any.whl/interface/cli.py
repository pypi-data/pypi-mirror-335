import subprocess
import os
import click

@click.command()
def main():
    """
    Launches the Testronaut Node-based animated CLI.
    """
    # Get the absolute path to index.js
    js_path = os.path.join(os.path.dirname(__file__), "index.js")

    try:
        subprocess.run(["node", js_path], check=True)
    except FileNotFoundError:
        click.echo("❌ Node.js is not installed or not found in PATH.")
    except subprocess.CalledProcessError as e:
        click.echo(f"❌ Error running index.js: {e}")
