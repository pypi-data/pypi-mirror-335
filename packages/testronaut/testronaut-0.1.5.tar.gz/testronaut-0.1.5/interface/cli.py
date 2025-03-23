import subprocess
import os
import click

@click.command()
def main():
    """
    Launch the Node.js CLI (index.mjs) after ensuring node_modules is installed.
    """
    js_dir = os.path.dirname(__file__)
    js_file = os.path.join(js_dir, "index.js")
    node_modules = os.path.join(js_dir, "node_modules")
    package_json = os.path.join(js_dir, "package.json")

    if not os.path.exists(package_json):
        click.echo("❌ package.json not found. Cannot install Node dependencies.")
        return

    if not os.path.exists(node_modules):
        click.echo("📦 Installing Node.js dependencies for Testronaut...")
        try:
            subprocess.run(["npm", "install"], cwd=js_dir, check=True)
        except subprocess.CalledProcessError as e:
            click.echo(f"❌ npm install failed: {e}")
            return

    # Now run index.mjs
    try:
        subprocess.run(["node", js_file], check=True)
    except FileNotFoundError:
        click.echo("❌ Node.js is not installed or not found in PATH.")
    except subprocess.CalledProcessError as e:
        click.echo(f"❌ Error running index.mjs: {e}")

