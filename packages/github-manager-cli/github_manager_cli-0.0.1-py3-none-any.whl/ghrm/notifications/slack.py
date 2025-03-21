# slack.py - Sends notifications to Slack channels

import os
import requests
from rich.console import Console
from rich.markdown import Markdown

SLACK_WEBHOOK_URL = os.getenv("SLACK_WEBHOOK_URL")
console = Console()

def send_slack_notification(title, details, status="info"):
    """
    Sends a notification message to a Slack channel using a webhook.
    Args:
        title (str): The title of the message.
        details (dict or str): The details of the message.
        status (str): The status of the message (info, success, warning, error).

    Returns:
        response: Response object from the Slack API request.
    """
    if not SLACK_WEBHOOK_URL:
        console.print("[bold red]Error: SLACK_WEBHOOK_URL is not configured.[/bold red]")
        return None

    # Define colors for different statuses
    colors = {
        "success": "#36a64f",  # Green
        "warning": "#ffcc00",  # Yellow
        "error": "#ff0000",    # Red
        "info": "#0000ff"      # Blue
    }

    # Create the message
    if isinstance(details, dict):
        details_str = "\n".join([f"*{key}*: {value}" for key, value in details.items()])
    else:
        details_str = details

    markdown_message = f"*{title}*\n{details_str}"
    payload = {
        "attachments": [
            {
                "color": colors.get(status, "#0000ff"),
                "text": markdown_message
            }
        ]
    }

    response = requests.post(SLACK_WEBHOOK_URL, json=payload)

    if response.status_code == 200:
        console.print("[bold green]Notification sent successfully.[/bold green]")
    else:
        console.print(f"[bold red]Failed to send notification. Status code: {response.status_code}[/bold red]")
    return response

def format_recommendations_for_notification(recommendations):
    """
    Formats recommendations as a message for notifications.
    Args:
        recommendations (list): List of recommendation strings.

    Returns:
        str: Formatted message for notifications.
    """
    formatted_message = "Cost Optimization Recommendations:\n" + "\n".join(recommendations)
    return formatted_message
