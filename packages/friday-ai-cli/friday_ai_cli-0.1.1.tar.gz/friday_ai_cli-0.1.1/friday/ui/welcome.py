from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich.align import Align
from datetime import datetime
import pyfiglet
import platform
import os

console = Console()


def create_ascii_art():
    """Create FRIDAY ASCII art with doom font and orange color"""
    # Use doom font for the ASCII art
    ascii_art = pyfiglet.figlet_format("FRIDAY AI CLI", font="doom")
    # Create text with explicit hex color for orange
    return Text(ascii_art, style="bold #FF8C00")  # Using a bright orange hex color


def create_info_panel():
    """Create information panel"""
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    current_dir = os.getcwd()
    info_text = Text.assemble(
        ("Version: ", "bold white"),
        ("0.1.0\n", "cyan"),
        ("Status: ", "bold white"),
        ("Active\n", "green"),
        ("Model: ", "bold white"),
        ("Claude 3 Sonnet (2025-02-19)\n", "magenta"),
        ("Working Directory: ", "bold white"),
        (f"{current_dir}\n", "yellow"),
        ("Time: ", "bold white"),
        (f"{current_time}\n", "cyan"),
        ("\nSystem: ", "bold white"),
        (f"{platform.system()} {platform.release()}\n", "cyan"),
        ("Python: ", "bold white"),
        (f"{platform.python_version()}\n", "cyan"),
    )
    return Panel(
        info_text,
        title="System Info",
        border_style="#FF8C00",
        padding=(1, 2),
    )


def create_welcome_message():
    """Create welcome message"""
    message = Text.assemble(
        ("\n👋 Welcome to FRIDAY AI CLI!\n", "bold cyan"),
        ("(Forget Refactoring, I Do All Your Coding Now!)\n\n", "cyan"),
        (
            "I'm your AI-powered development assistant, created by Yash and powered by Claude 3.\n",
            "white",
        ),
        ("I'm here to help you build great software efficiently.\n\n", "white"),
        ("Available Tools:\n", "bold white"),
        (
            "🛠  Bash Tool - System operations, package management, and build tasks\n",
            "green",
        ),
        (
            "📝 Edit Tool - File operations, code management, and project structure\n",
            "blue",
        ),
        ("\nTips:", "bold yellow"),
        ("\n• Use Ctrl+C to exit the chat session", "yellow"),
        ("\n• Start with your project goals or specific tasks", "yellow"),
        ("\n• I'll always explain my approach before taking action\n", "yellow"),
    )
    return Panel(
        Align.left(message),
        border_style="#FF8C00",
        padding=(1, 2),
    )


def show_welcome_screen():
    """Display the welcome screen"""
    console.clear()

    # Create and display ASCII art
    ascii_art = create_ascii_art()
    console.print(Align.center(ascii_art))

    # Create and display info panel
    info_panel = create_info_panel()
    console.print(info_panel)

    # Create and display welcome message
    welcome_message = create_welcome_message()
    console.print(welcome_message)

    # Add some spacing
    console.print("\n")
