# display.py - Display module for GitHub Manager CLI

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.style import Style
from rich.text import Text

# Initialize Rich console
console = Console()

def display_result(message, status="success"):
    # Define styles for different status types
    styles = {
        "success": "green",
        "error": "red",
        "info": "blue",
        "warning": "yellow"
    }

    style = styles.get(status, "white")

    # Create panel with appropriate styling
    panel = Panel(
        message,
        border_style=style,
        title="[bold]GitHub Manager[/bold]",
        padding=(1, 2)
    )

    console.print("\n")
    console.print(panel)
    console.print("\n")

def display_list(title, items, columns):
    """Display items in a rich table format"""
    table = Table(title=title, show_header=True, header_style="bold magenta", border_style="blue")

    # Add columns
    for column in columns:
        table.add_column(column, style="cyan")

    # Add rows
    for item in items:
        table.add_row(*[str(i) for i in item])

    console.print(table)

def display_empty(message):
    """Display message for empty results"""
    console.print(f"[italic]{message}[/italic]")
