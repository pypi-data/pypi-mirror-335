# discord.py - Sends notifications to Discord channels

import os
from datetime import datetime
import requests
from rich.console import Console

console = Console()

class DiscordNotifier:
    def __init__(self):
        self.webhook_url = os.getenv('DISCORD_WEBHOOK_URL')
        if not self.webhook_url:
            console.print("[bold red]Warning: DISCORD_WEBHOOK_URL not set. Notifications will be disabled.[/bold red]")

    def send_discord_notification(self, title, description, color=0x00ff00, fields=None):
        """
        Send notification to Discord channel
        color: Discord color code (default: green)
        fields: List of dicts with name and value pairs
        """
        if not self.webhook_url:
            return

        embed = {
            "title": title,
            "description": description,
            "color": color,
            "timestamp": datetime.utcnow().isoformat(),
            "fields": fields or []
        }

        data = {
            "embeds": [embed]
        }

        try:
            response = requests.post(
                self.webhook_url,
                json=data
            )
            response.raise_for_status()
        except requests.exceptions.RequestException as e:
            console.print(f"[bold red]Failed to send Discord notification: {str(e)}[/bold red]")

def send_discord_notification(action, details, status="success"):
    """Helper function to create and send notifications"""
    notifier = DiscordNotifier()

    # Define colors for different statuses
    colors = {
        "success": 0x00ff00,  # Green
        "warning": 0xffff00,  # Yellow
        "error": 0xff0000,    # Red
        "info": 0x0000ff     # Blue
    }

    # Create fields based on details
    fields = []
    if isinstance(details, dict):
        fields = [
            {"name": key, "value": str(value), "inline": True}
            for key, value in details.items()
        ]

    notifier.send_discord_notification(
        title=f"GitHub Manager: {action}",
        description=str(details) if not isinstance(details, dict) else None,
        color=colors.get(status, 0x00ff00),
        fields=fields if fields else None
    )
