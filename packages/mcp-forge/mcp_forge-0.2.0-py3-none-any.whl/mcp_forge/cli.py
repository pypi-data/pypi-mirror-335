"""Command line interface for MCP server scaffolding."""

import click
from rich.console import Console
from rich.panel import Panel
from rich.text import Text

from .generators.base import create_new_server
from .generators.feature import add_feature
from .utils.template import list_available_features

console = Console()


@click.group()
def main():
    """MCP Server Scaffolding Tool - Create and extend MCP servers with ease."""
    pass


@main.command()
@click.argument("project_name")
@click.option("--description", "-d", help="Project description")
@click.option("--python-version", "-p", default=">=3.10", help="Python version requirement")
def new(project_name: str, description: str, python_version: str):
    """Create a new MCP server project."""
    try:
        create_new_server(project_name=project_name, description=description or f"{project_name} MCP server", python_version=python_version)
        console.print(
            Panel(Text(f"✨ Successfully created new MCP server: {project_name}", style="green"), title="[bold green]Success[/bold green]")
        )
    except Exception as e:
        console.print(Panel(Text(str(e), style="red"), title="[bold red]Error[/bold red]"))


@main.command()
@click.argument("tool_name")
@click.option("--description", "-d", help="Tool description (optional)")
def add(tool_name: str, description: str):
    """Add a new tool template to an existing MCP server.

    Generates a simple tool with a basic input schema that can be customized.
    """
    try:
        add_feature(tool_name)
        console.print(Panel(Text(f"✨ Successfully added tool: {tool_name}", style="green"), title="[bold green]Success[/bold green]"))
    except Exception as e:
        console.print(Panel(Text(str(e), style="red"), title="[bold red]Error[/bold red]"))


@main.command()
def list():
    """List available features that can be added to an MCP server."""
    features = list_available_features()
    console.print(
        Panel(
            "\n".join([f"• [cyan]{feature}[/cyan]" for feature in features]), title="[bold]Available Features[/bold]", border_style="blue"
        )
    )


if __name__ == "__main__":
    main()
