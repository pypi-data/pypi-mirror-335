import sys
import click
import os
import shutil
import subprocess

# Ensure correct template path
TEMPLATES_DIR = os.path.dirname(__file__)

def check_requirements():
    """Checks if Python 3.12+, pip 25+, and Poetry are installed, otherwise handles installation."""
    
    # Check Python version
    if sys.version_info < (3, 12):
        click.echo("❌ Python 3.12 or higher is required to run this tool.")
        sys.exit(1)

    # Check pip version
    try:
        pip_version = subprocess.run(["pip", "--version"], capture_output=True, text=True)
        pip_version_number = float(pip_version.stdout.split()[1].split(".")[0])  # Get major version
        
        if pip_version_number < 25:
            click.echo(f"❌ pip 25 or higher is required. Found: pip {pip_version_number}")
            sys.exit(1)
    except Exception:
        click.echo("❌ pip is not installed or not accessible.")
        sys.exit(1)

    # Check if Poetry is installed
    try:
        subprocess.run(["poetry", "--version"], capture_output=True, text=True, check=True)
    except FileNotFoundError:
        click.echo("⚠️ Poetry is not installed.")
        install_poetry = click.confirm("Would you like to install Poetry now?", default=True)
        if install_poetry:
            install_poetry_command()
        else:
            click.echo("❌ Poetry is required. Please install it manually.")
            sys.exit(1)

    # If all checks pass, log success
    click.echo("✅ Python, pip, and Poetry meet the requirements.")

def install_poetry_command():
    """Installs Poetry automatically."""
    click.echo("🚀 Installing Poetry...")
    try:
        subprocess.run(["curl", "-sSL", "https://install.python-poetry.org", "|", "python3", "-"], shell=True, check=True)
        click.echo("✅ Poetry installed successfully!")
    except subprocess.CalledProcessError:
        click.echo("❌ Failed to install Poetry. Please install it manually.")
        sys.exit(1)

# Run version check before anything else
check_requirements()

@click.group()
def cli():
    """MyTool CLI - A Python CLI tool for project scaffolding"""
    pass

@click.command()
@click.argument("project_name", required=False)
def create_project(project_name):
    """Creates a new project using a selected template"""

    # Get available templates
    templates = [t for t in os.listdir(TEMPLATES_DIR) if os.path.isdir(os.path.join(TEMPLATES_DIR, t)) and not t.startswith("__")]

    if not templates:
        click.echo("No templates available.")
        return

    # Show template choices
    click.echo("Select a template:")
    for i, template in enumerate(templates, 1):
        click.echo(f"{i}. {template}")

    # Ask user to choose a template
    choice = click.prompt("Enter the number of the template", type=int, default=1)

    # Validate the choice
    if choice < 1 or choice > len(templates):
        click.echo("Invalid choice. Exiting.")
        return

    template_name = templates[choice - 1]  # Get the chosen template name

    # Ask for project name if not provided
    if not project_name:
        project_name = click.prompt("Enter the project name", type=str)

    template_path = os.path.join(TEMPLATES_DIR, template_name)

    os.makedirs(project_name, exist_ok=True)

    for item in os.listdir(template_path):
        s = os.path.join(template_path, item)
        d = os.path.join(project_name, item)
        if os.path.isdir(s):
            shutil.copytree(s, d, dirs_exist_ok=True)
        else:
            shutil.copy2(s, d)

    click.echo(f"✅ Project '{project_name}' created successfully using template '{template_name}'!")

    # Run `poetry install` inside the created project
    try:
        click.echo("🚀 Running 'poetry install' in the new project...")
        subprocess.run(["poetry", "install"], cwd=project_name, check=True)
        click.echo("✅ Poetry dependencies installed successfully!")
    except subprocess.CalledProcessError:
        click.echo("❌ Failed to install dependencies with Poetry. Please check manually.")

# Register commands
cli.add_command(create_project)

# Entry point for Poetry
def main():
    cli()

if __name__ == "__main__":
    main()
