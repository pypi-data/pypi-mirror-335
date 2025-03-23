from rich.console import Console
from rich.prompt import Prompt
from rich.markdown import Markdown
from rich.panel import Panel
from rich.syntax import Syntax
from datetime import datetime
from typing import Optional, Any
from anthropic.types import TextBlock
from anthropic.types.beta import BetaTextBlock, BetaToolUseBlock
import os

DEV_MODE = os.getenv("DEV_MODE", "false").lower() == "true"


class FridayTerminal:
    def __init__(self):
        self.console = Console()
        self.styles = {
            "user": "bold cyan",
            "assistant": "bold green",
            "tool": "bold yellow",
            "tool_output": "bold blue",
            "error": "bold red",
            "thinking": "bold magenta",
        }
        self.prefixes = {
            "user": "👤 [User]",
            "assistant": "🤖 [FRIDAY]",
            "tool": "🔧 [Tool]",
            "tool_output": "📤 [Tool Output]",
            "error": "❌ [Error]",
            "thinking": "🤔 [Thinking]",
        }

    def format_assistant_message(self, message: Any) -> None:
        """Format and print assistant's message"""
        if isinstance(message, (TextBlock, BetaTextBlock)):
            self._format_response(message.text, "assistant")
        elif isinstance(message, BetaToolUseBlock):
            self.console.print("")  # Add spacing
            self.console.print(
                Panel(
                    str(message.input),
                    border_style=self.styles["tool"],
                    title=self.prefixes["tool"],
                    title_align="left",
                    padding=(1, 2),
                )
            )
        elif isinstance(message, dict) and message.get("type") == "thinking":
            if DEV_MODE:  # Only show thinking output in development mode
                self.console.print("")  # Add spacing
                self.console.print(
                    Panel(
                        f"{message.get('thinking', 'Processing...')}",
                        border_style=self.styles["thinking"],
                        title=self.prefixes["thinking"],
                        title_align="left",
                        padding=(1, 2),
                    )
                )
        elif isinstance(message, str):
            self._format_response(message, "assistant")
        else:
            self._format_response(str(message), "assistant")

    def format_tool_output(self, output: Any, tool_id: str) -> None:
        """Format and print tool output"""
        self.console.print("")  # Add spacing

        if hasattr(output, "output") and output.output:
            # Format command output with proper highlighting
            output_text = output.output
            if output_text.startswith("$") or output_text.startswith("#"):
                # This might be a command output, format accordingly
                parts = output_text.split("\n")
                formatted_parts = []
                for part in parts:
                    if part.startswith("$") or part.startswith("#"):
                        formatted_parts.append(f"[bold white]{part}[/]")
                    else:
                        formatted_parts.append(part)
                output_text = "\n".join(formatted_parts)

            self.console.print(
                Panel(
                    output_text,
                    border_style=self.styles["tool_output"],
                    title=f"{self.prefixes['tool_output']} ({tool_id})",
                    title_align="left",
                    padding=(1, 2),
                )
            )

        if hasattr(output, "error") and output.error:
            self.console.print(
                Panel(
                    output.error,
                    border_style=self.styles["error"],
                    title=self.prefixes["error"],
                    title_align="left",
                    padding=(1, 2),
                )
            )

        if hasattr(output, "base64_image") and output.base64_image:
            self.console.print(
                f"[{self.styles['tool_output']}]📸 Image content received[/]"
            )

    def _format_response(self, response: str, message_type: str) -> None:
        """Format and print FRIDAY's response"""
        self.console.print("")  # Add spacing

        if "```" in response:
            parts = response.split("```")
            for i, part in enumerate(parts):
                if i % 2 == 0:  # Regular text
                    if part.strip():
                        self.console.print(
                            Panel(
                                Markdown(part.strip()),
                                border_style=self.styles[message_type],
                                title=self.prefixes[message_type],
                                title_align="left",
                                padding=(1, 2),
                            )
                        )
                else:  # Code block
                    lang = part.split("\n")[0] if part.split("\n")[0] else "python"
                    code = "\n".join(part.split("\n")[1:])
                    self.console.print(
                        Panel(
                            Syntax(code.strip(), lang, theme="monokai"),
                            border_style="cyan",
                            title=f"📝 {lang.capitalize()} Code",
                            title_align="left",
                            padding=(1, 2),
                        )
                    )
        else:
            self.console.print(
                Panel(
                    Markdown(response),
                    border_style=self.styles[message_type],
                    title=self.prefixes[message_type],
                    title_align="left",
                    padding=(1, 2),
                )
            )
