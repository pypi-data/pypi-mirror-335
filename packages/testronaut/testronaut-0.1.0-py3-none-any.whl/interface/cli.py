import click
from interface.menu import (
    build_test_cases,
    code_review,
    create_documentation,
    refactor_code
)

@click.group()
def main():
    """Grizzly7 CLI — Rizz up your CI/CD with test generation, code review, and more."""
    pass

@main.command()
def test():
    """Build integration test cases using AI."""
    click.echo(">>> Generating integration tests...")
    build_test_cases()

@main.command()
def review():
    """Review your code performance & structure."""
    click.echo(">>> Running code review...")
    code_review()

@main.command()
def docs():
    """Generate documentation from your codebase."""
    click.echo(">>> Creating documentation...")
    create_documentation()

@main.command()
def refactor():
    """Suggest or apply refactoring to your code."""
    click.echo(">>> Refactoring your code...")
    refactor_code()
