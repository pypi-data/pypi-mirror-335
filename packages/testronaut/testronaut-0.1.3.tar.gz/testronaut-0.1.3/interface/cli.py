import subprocess
import os
import click

@click.command()
def main():
    """
    Launches the Node-based Testronaut animated CLI.
    """
    js_dir = os.path.dirname(__file__)
    js_file = os.path.join(js_dir, "index.mjs")
    node_modules = os.path.join(js_dir, "node_modules")

    # Auto-install Node deps if not present
    if not os.path.exists(node_modules):
        click.echo("📦 Setting up Testronaut's Node dependencies...")
        subprocess.run(["npm", "install"], cwd=js_dir)

    try:
        subprocess.run(["node", js_file], check=True)
    except FileNotFoundError:
        click.echo("❌ Node.js is not installed or not found in PATH.")
    except subprocess.CalledProcessError as e:
        click.echo(f"❌ Error running index.mjs: {e}")

