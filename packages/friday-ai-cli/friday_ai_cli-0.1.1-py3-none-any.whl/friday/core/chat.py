from .tools import ToolResult
from anthropic.types import RateLimitError
from anthropic.types.beta import BetaContentBlockParam
from colorama import init
import traceback
from datetime import timedelta
import httpx
from typing import cast
from enum import Enum

# Initialize colorama
init(autoreset=True)
DEV_MODE = False  # Set to True to show thinking output


class Sender(Enum):
    USER = "user"
    BOT = "assistant"
    TOOL = "tool"


def _api_response_callback(
    request: httpx.Request,
    response: httpx.Response | object | None,
    error: Exception | None,
    response_state: dict[str, tuple[httpx.Request, httpx.Response | object | None]],
):
    """
    Handle an API response by storing it to state and rendering it.
    """
    # response_id = datetime.now().isoformat()
    # response_state[response_id] = (request, response)
    if error:
        _render_error(error)

    # _render_api_response(request, response, response_id)
    # not rendering anything except error as this over complicate the interface
    pass


def _tool_output_callback(
    tool_output: ToolResult, tool_id: str, tool_state: dict[str, ToolResult]
):
    """Handle a tool output by storing it to state and rendering it."""
    tool_state[tool_id] = tool_output
    _render_message(Sender.TOOL, tool_output)


def _render_api_response(
    request: httpx.Request,
    response: httpx.Response | object | None,
    response_id: str,
):
    from rich.console import Console
    from rich.panel import Panel
    from rich.markdown import Markdown
    from rich.syntax import Syntax

    console = Console()

    # Format request details
    request_details = [
        f"Method: `{request.method}`",
        f"URL: `{request.url}`",
        "\nHeaders:",
        *[f"- `{k}: {v}`" for k, v in request.headers.items()],
        "\nBody:",
        "```",
        request.read().decode(),
        "```",
    ]

    # Print request panel
    console.print("")
    console.print(
        Panel(
            Markdown("\n".join(request_details)),
            border_style="yellow",
            title="📡 [API Request]",
            title_align="left",
            padding=(1, 2),
        )
    )

    # Format and print response
    if isinstance(response, httpx.Response):
        response_details = [
            f"Status: `{response.status_code}`",
            "\nHeaders:",
            *[f"- `{k}: {v}`" for k, v in response.headers.items()],
            "\nBody:",
            "```json",
            response.text,
            "```",
        ]

        console.print(
            Panel(
                Markdown("\n".join(response_details)),
                border_style="green",
                title="📥 [API Response]",
                title_align="left",
                padding=(1, 2),
            )
        )
    elif response is not None:
        console.print(
            Panel(
                str(response),
                border_style="yellow",
                title="📥 [API Response]",
                title_align="left",
                padding=(1, 2),
            )
        )


def _render_error(error: Exception):
    from rich.console import Console
    from rich.panel import Panel
    from rich.markdown import Markdown

    console = Console()

    if isinstance(error, RateLimitError):
        body = "You have been rate limited."
        if retry_after := error.response.headers.get("retry-after"):
            body += (
                f"\nRetry after {str(timedelta(seconds=int(retry_after)))} (HH:MM:SS)."
            )
            body += "\nSee our API documentation for more details: https://docs.anthropic.com/en/api/rate-limits"
        body += f"\n\n{error.message}"
    else:
        body = str(error)
        body += "\n\n**Traceback:**"
        lines = "\n".join(traceback.format_exception(error))
        body += f"\n```python\n{lines}\n```"

    console.print("")  # Add spacing
    console.print(
        Panel(
            Markdown(f"**{error.__class__.__name__}**\n\n{body}"),
            border_style="red",
            title="❌ [Error]",
            title_align="left",
            padding=(1, 2),
        )
    )


def _render_message(
    sender: Sender,
    message: str | BetaContentBlockParam | ToolResult,
):
    """Convert input from the user or output from the agent to a formatted message."""
    from rich.console import Console
    from rich.panel import Panel
    from rich.markdown import Markdown
    from rich.syntax import Syntax
    import json

    console = Console()

    styles = {Sender.USER: "cyan", Sender.BOT: "green", Sender.TOOL: "yellow"}

    prefixes = {
        Sender.USER: "👤 [User]",
        Sender.BOT: "🤖 [FRIDAY]",
        Sender.TOOL: "🔧 [Tool]",
    }

    def print_panel(content, style, title, lang=None):
        """Helper to print consistent panels"""
        console.print("")  # Add spacing
        if lang:
            console.print(
                Panel(
                    Syntax(content, lang),
                    border_style=style,
                    title=title,
                    title_align="left",
                    padding=(1, 2),
                )
            )
        else:
            console.print(
                Panel(
                    Markdown(content),
                    border_style=style,
                    title=title,
                    title_align="left",
                    padding=(1, 2),
                )
            )

    # Handle tool results
    is_tool_result = not isinstance(message, str | dict)
    if not message or (
        is_tool_result
        and not hasattr(message, "error")
        and not hasattr(message, "output")
    ):
        return

    if is_tool_result:
        message = cast(ToolResult, message)
        if message.output:
            # Format command output specially
            output_text = message.output
            if output_text.startswith("$") or output_text.startswith("#"):
                parts = output_text.split("\n")
                formatted_parts = []
                for part in parts:
                    if part.startswith("$") or part.startswith("#"):
                        formatted_parts.append(f"`{part}`")
                    else:
                        formatted_parts.append(part)
                output_text = "\n".join(formatted_parts)

            print_panel(output_text, "blue", "📤 [Tool Output]")

        if message.error:
            print_panel(message.error, "red", "❌ [Error]")

    elif isinstance(message, dict):
        if message["type"] == "text":
            print_panel(message["text"], styles[sender], prefixes[sender])
        elif message["type"] == "thinking" and DEV_MODE:
            thinking_content = message.get("thinking", "Processing...")
            print_panel(thinking_content, "magenta", "🤔 [Thinking]")
        elif message["type"] == "tool_use":
            if isinstance(message, dict):
                print_text = json.dumps(message, indent=4)
                lang = "json"
            else:
                print_text = str(message)
                lang = None

            print_panel(
                print_text, styles[Sender.TOOL], prefixes[Sender.TOOL], lang=lang
            )
    else:
        print_panel(str(message), styles[sender], prefixes[sender])
