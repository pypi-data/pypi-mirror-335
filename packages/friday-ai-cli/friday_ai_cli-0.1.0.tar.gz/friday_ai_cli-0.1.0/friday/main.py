import typer
import asyncio
import os
import httpx
import dotenv
import logging
from rich.console import Console
from typing import Optional, Dict, Tuple, Any
from functools import partial
from .ui.welcome import show_welcome_screen

# Configure logging
logging.basicConfig(level=logging.ERROR)
logger = logging.getLogger("friday-main")

# Try to load environment variables from .env file
# Check common locations for .env file
env_locations = [
    "./.env",  # Current directory
    "~/.friday/.env",  # User's friday config directory
    os.path.join(
        os.path.dirname(os.path.abspath(__file__)), "..", ".env"
    ),  # Project root
]

for env_path in env_locations:
    expanded_path = os.path.expanduser(env_path)
    if os.path.exists(expanded_path):
        dotenv.load_dotenv(expanded_path)
        break

from .license.cli import (
    add_license_command,
    reset_license_command,
    check_license_on_startup,
    show_license_info,
)


# Define MODEL constant here to avoid import
MODEL_3_7 = "claude-3-7-sonnet-20250219"

app = typer.Typer(
    name="FRIDAY AI CLI",
    help="Your AI-powered software development assistant",
    add_completion=False,
)

console = Console()

# Global state for storing responses and tool outputs
response_state: Dict[str, Tuple[httpx.Request, Any]] = {}
tool_state = {}


async def start_chat_session(api_key: Optional[str] = None):
    """Initialize and start the chat session"""
    messages = []

    # First priority: command-line provided API key
    if api_key:
        # Verify the API key if provided directly
        console.print("Verifying provided API key...")
        is_valid, message = verify_anthropic_token(api_key)
        if is_valid:
            console.print("[green]API key is valid.[/green]")
            # Save for future use
            save_api_key(api_key)
            console.print("[green]API key saved for future use.[/green]")
        else:
            console.print(f"[red]Invalid API key: {message}[/red]")
            console.print("[yellow]Please provide a valid Anthropic API key.[/yellow]")
            return

    # Second priority: environment variable
    elif os.getenv("ANTHROPIC_API_KEY"):
        api_key = os.getenv("ANTHROPIC_API_KEY")
        console.print("Using API key from environment variable.")

    # Third priority: saved API key
    elif load_api_key():
        api_key = load_api_key()
        console.print("Using saved API key.")

    # Last resort: prompt the user
    else:
        console.print(
            "[yellow]No API key found. You need an Anthropic API key to use FRIDAY.[/yellow]"
        )
        console.print(
            "[yellow]You can get one at https://console.anthropic.com/[/yellow]"
        )
        console.print("Your API key will be saved securely for future use.")
        api_key = typer.prompt("Enter your Anthropic API Key", hide_input=True)

        # Verify the newly entered API key
        console.print("Verifying API key...")
        is_valid, message = verify_anthropic_token(api_key)
        if is_valid:
            console.print("[green]API key is valid.[/green]")
            # Save for future use
            save_api_key(api_key)
            console.print("[green]API key saved for future use.[/green]")
        else:
            console.print(f"[red]Invalid API key: {message}[/red]")
            console.print(
                "[yellow]Please provide a valid Anthropic API key and try again.[/yellow]"
            )
            return

    # Preload all encrypted modules directly into memory
    try:
        from .license.crypto import decrypt_all_modules
        import sys

        console.print("Preparing FRIDAY components...")

        # Preload modules directly into sys.modules
        preload_sys_modules = True
        success, result = decrypt_all_modules(preload_sys_modules=preload_sys_modules)

        if not success:
            error = result.get("error", "Unknown error loading components")
            console.print(f"[yellow]Warning: {error}[/yellow]")
    except Exception as e:
        console.print(
            f"[yellow]Warning: Could not prepare FRIDAY components: {str(e)}[/yellow]"
        )

    # Now import the core modules - should work directly from memory
    try:
        # Access modules directly from sys.modules when possible
        if "friday.core.engine" in sys.modules and hasattr(
            sys.modules["friday.core.engine"], "run_ai"
        ):
            run_ai = sys.modules["friday.core.engine"].run_ai
        else:
            # Fallback to regular import
            from .core.engine import run_ai

        if "friday.core.chat" in sys.modules:
            chat_module = sys.modules["friday.core.chat"]
            Sender = getattr(chat_module, "Sender", None)
            _render_message = getattr(chat_module, "_render_message", None)
            _tool_output_callback = getattr(chat_module, "_tool_output_callback", None)
            _api_response_callback = getattr(
                chat_module, "_api_response_callback", None
            )

            # Fix for the Sender enum if it doesn't exist properly
            if Sender is None:
                from enum import Enum

                # Create the Sender enum directly in the chat module
                Sender = Enum("Sender", ["USER", "BOT"])
                chat_module.Sender = Sender
            elif not hasattr(Sender, "BOT"):
                from enum import Enum

                # Replace with a proper enum if it exists but is incomplete
                Sender = Enum("Sender", ["USER", "BOT"])
                chat_module.Sender = Sender
        else:
            # Fallback to regular import
            try:
                from .core.chat import (
                    Sender,
                    _render_message,
                    _tool_output_callback,
                    _api_response_callback,
                )
            except ImportError as e:
                from enum import Enum

                # Create fallback implementations if imports fail
                Sender = Enum("Sender", ["USER", "BOT"])
                _render_message = lambda sender, text: console.print(
                    f"[{'blue' if sender == Sender.USER else 'green'}]{text}[/]"
                )
                _tool_output_callback = lambda tool_name, output: console.print(
                    f"[dim]Tool {tool_name}: {output}[/dim]"
                )
                _api_response_callback = lambda response: None

    except ImportError as e:
        console.print(f"\n[red]Error importing core modules: {str(e)}[/red]")
        console.print(
            "\n[yellow]This might indicate an issue with your license or decryption.[/yellow]"
        )
        console.print(
            "[yellow]Try running 'friday add-license YOUR_LICENSE_KEY' again to refresh credentials.[/yellow]"
        )
        raise

    # Start the chat loop
    try:
        while True:
            # Add a newline for spacing
            console.print("")
            # Get user input with styled prompt
            user_input = typer.prompt("👤 You: ", prompt_suffix=" ›")
            # Add a newline for spacing
            console.print("")

            if user_input.lower() in {"exit", "quit"}:
                console.print("\n[yellow]Goodbye! Have a great day! 👋[/yellow]")
                break

            # Add user message to conversation
            messages.append({"role": "user", "content": user_input})
            try:
                # Run the sampling loop
                messages = await run_ai(
                    messages=messages,
                    output_callback=partial(_render_message, Sender.BOT),
                    tool_output_callback=partial(
                        _tool_output_callback, tool_state=tool_state
                    ),
                    api_response_callback=partial(
                        _api_response_callback, response_state=response_state
                    ),
                    api_key=api_key,
                )
            except Exception as e:
                console.print(f"\n[red]Error during message processing: {str(e)}[/red]")
                if hasattr(e, "response"):
                    console.print(
                        f"[red]Response status: {e.response.status_code}[/red]"
                    )
                    console.print(f"[red]Response body: {e.response.text}[/red]")
                raise
    except KeyboardInterrupt:
        console.print("\n[yellow]Goodbye! Have a great day! 👋[/yellow]")
    except Exception as e:
        console.print(f"\n[red]Fatal error: {str(e)}[/red]")


def get_api_key_path():
    """Returns the path to the API key file"""
    # Store in the .friday directory in user's home
    friday_dir = os.path.expanduser("~/.friday")
    os.makedirs(friday_dir, exist_ok=True)
    return os.path.join(friday_dir, ".anthropic_key")


def save_api_key(api_key):
    """Save the Anthropic API key to a file

    Args:
        api_key (str): The API key to save

    Returns:
        bool: True if successful, False otherwise
    """
    try:
        api_key_path = get_api_key_path()
        with open(api_key_path, "w") as f:
            f.write(api_key)
        # Set permissions to be readable only by the user
        os.chmod(api_key_path, 0o600)
        return True
    except Exception as e:
        logger.error(f"Failed to save API key: {e}")
        return False


def load_api_key():
    """Load the saved Anthropic API key

    Returns:
        str or None: The API key if found, None otherwise
    """
    api_key_path = get_api_key_path()
    if os.path.exists(api_key_path):
        try:
            with open(api_key_path, "r") as f:
                return f.read().strip()
        except Exception as e:
            logger.error(f"Error reading API key: {e}")
    return None


def verify_anthropic_token(api_token):
    """
    Verify the Anthropic API token using the Anthropic SDK.

    Args:
        api_token (str): Your Anthropic API token.

    Returns:
        tuple: (is_valid, message) where is_valid is a boolean indicating
               whether the token is valid, and message provides details.
    """
    try:
        from anthropic import Client

        # Initialize the client with the provided token.
        client = Client(api_key=api_token)

        # Make a minimal API call.
        # Adjust the prompt, model, or parameters as needed.
        response = client.messages.create(
            model=MODEL_3_7,
            system="RETURN PONG! WHEN YOU SEE PING!",
            max_tokens=10,
            messages=[
                {
                    "role": "user",
                    "content": "PING!",
                }
            ],
        )

        # If a valid response is returned, assume the token is valid.
        if response:
            return True, "API key is valid"
        else:
            return False, "API key validation returned no response"
    except Exception as e:
        # An exception is likely due to an invalid token or Account not having balance.
        return False, f"Token verification failed: {str(e)}"


@app.command()
def chat(
    api_key: str = typer.Option(
        None,
        "--api-key",
        "-k",
        help="Anthropic API Key (will be saved for future use if valid)",
    ),
):
    """Start a chat session with FRIDAY

    If you don't provide an API key, FRIDAY will:
    1. Look for a previously saved API key
    2. Check for the ANTHROPIC_API_KEY environment variable
    3. Prompt you to enter a key (which will be saved for future use)

    You can set your API key once using: friday set-api-key YOUR_API_KEY
    """
    # Check license before starting chat
    if check_license_on_startup():
        show_welcome_screen()
        asyncio.run(start_chat_session(api_key))
    else:
        console.print(
            "\n[yellow]Please add a valid license to use FRIDAY AI CLI.[/yellow]"
        )
        console.print(
            "[green]Run [bold]friday add-license <YOUR_LICENSE_KEY>[/bold] to activate.[/green]"
        )


@app.command()
def version():
    """Show FRIDAY AI CLI version and configuration"""
    console.print("[cyan]FRIDAY AI CLI[/cyan] [green]v0.1.0[/green]")
    console.print(
        f"\n[white]Using Claude Model:[/white] [magenta]{MODEL_3_7}[/magenta]"
    )
    console.print("[white]Developed by:[/white] [yellow]Yash[/yellow]")

    # Display API key information
    console.print("\n[bold]API Key:[/bold]")
    api_key = load_api_key()
    if api_key:
        # Show first 4 and last 4 characters of the API key
        masked_key = f"{api_key[:4]}...{api_key[-4:]}" if len(api_key) > 8 else "****"
        console.print(f"[green]✓ API Key configured:[/green] [dim]{masked_key}[/dim]")
        console.print("[dim]Use 'friday reset-api-key' to remove saved key[/dim]")
    else:
        env_key = os.getenv("ANTHROPIC_API_KEY")
        if env_key:
            masked_key = (
                f"{env_key[:4]}...{env_key[-4:]}" if len(env_key) > 8 else "****"
            )
            console.print(
                f"[green]✓ Using API Key from environment:[/green] [dim]{masked_key}[/dim]"
            )
        else:
            console.print("[yellow]No API key configured yet.[/yellow]")
            console.print(
                "[yellow]You'll be prompted for your Anthropic API key when starting chat.[/yellow]"
            )
            console.print(
                "[dim]Tip: Use 'friday set-api-key YOUR_API_KEY' to save your key[/dim]"
            )

    # Show license information alongside version
    try:
        console.print("\n[bold]License Status:[/bold]")
        show_license_info()
    except Exception as e:
        console.print(f"\n[red]Error retrieving license status: {str(e)}[/red]")
        console.print(
            "[yellow]Use 'friday add-license YOUR_LICENSE_KEY' to activate.[/yellow]"
        )


@app.command()
def add_license(license_key: str):
    """Add or update your FRIDAY license key"""
    add_license_command(license_key)
    show_license_info()


@app.command()
def reset_license():
    """Remove your current FRIDAY license key"""
    reset_license_command()


@app.command()
def set_api_key(api_key: str):
    """Set your Anthropic API key"""
    # Verify the API key
    console.print("Verifying API key...")
    is_valid, message = verify_anthropic_token(api_key)

    if is_valid:
        # Save the API key
        if save_api_key(api_key):
            console.print("[green]✓ API key verified and saved successfully![/green]")
            console.print(
                "You can now use 'friday chat' without providing the API key each time."
            )
        else:
            console.print("[red]✗ API key is valid but could not be saved.[/red]")
            console.print(
                "[yellow]You may need to use the --api-key option when running 'friday chat'.[/yellow]"
            )
    else:
        console.print(f"[red]✗ Invalid API key: {message}[/red]")
        console.print("[yellow]Please check your API key and try again.[/yellow]")


@app.command()
def reset_api_key():
    """Remove your saved Anthropic API key"""
    api_key_path = get_api_key_path()

    if os.path.exists(api_key_path):
        try:
            os.remove(api_key_path)
            console.print("[green]✓ API key removed successfully![/green]")
        except Exception as e:
            console.print(f"[red]✗ Error removing API key: {str(e)}[/red]")
    else:
        console.print("[yellow]No saved API key found.[/yellow]")


if __name__ == "__main__":
    app()
