from rich.live import Live
from rich.spinner import Spinner
from rich.console import Group, Console
from rich.panel import Panel
from rich.text import Text
import asyncio
import random

class FridayLoader:
    def __init__(self):
        self.console = Console()
        self.loading_messages = [
            "🤔 Analyzing your request...",
            "📚 Consulting best practices...",
            "⚡ Processing solution...",
            "🛠️ Preparing development environment...",
            "📝 Formulating response...",
            "🎯 Fine-tuning approach...",
            "🧩 Assembling components...",
            "🔧 Optimizing solution...",
        ]
        self._live = None

    def _get_loading_panel(self) -> Panel:
        """Get loading panel with spinner and message"""
        spinner = Spinner("dots", style="cyan")
        message = random.choice(self.loading_messages)
        
        return Panel(
            Group(spinner, Text("\n" + message)),
            title="🤖 FRIDAY",
            border_style="cyan",
            padding=(1, 2)
        )

    def start(self):
        """Start the loading animation"""
        if not self._live:
            self._live = Live(
                self._get_loading_panel(),
                console=self.console,
                refresh_per_second=4,
                transient=False
            )
            self._live.start()

    def stop(self):
        """Stop the loading animation"""
        if self._live:
            self._live.stop()
            self._live = None
