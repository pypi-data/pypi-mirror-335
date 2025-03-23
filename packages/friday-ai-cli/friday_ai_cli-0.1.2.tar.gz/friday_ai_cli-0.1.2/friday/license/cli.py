import typer
from rich.console import Console
from rich.panel import Panel
from rich.markdown import Markdown
from rich.table import Table
from typing import Optional
import datetime
import os

from .manager import (
    validate_license_key,
    save_license_key,
    get_saved_license_key,
    remove_license_key,
    get_license_status,
)

from .api_client import (
    authenticate,
    validate_license,
    get_decryption_credentials,
    clear_cache as clear_api_cache,
)

console = Console()


def add_license_command(license_key: str, use_api: bool = True):
    """Add or update a license key"""
    use_api_server = True == use_api

    # Show processing message
    with console.status("Validating license key..."):
        # Try to validate using the API server
        console.print("Connecting to license server...")
        is_valid, result = validate_license(license_key)

    if not is_valid:
        error_msg = result.get("error", "Invalid license key")
        console.print(
            Panel(
                Markdown(f"❌ **License Error**: {error_msg}"),
                border_style="red",
                title="License Validation Failed",
                title_align="left",
                padding=(1, 2),
            )
        )
        return

    # If we got here, the license is valid
    # Try to get decryption credentials if using API
    with console.status("Retrieving decryption credentials..."):
        creds_success, _ = get_decryption_credentials(license_key=license_key)

    # We need to always save the license, regardless of API or local validation
    try:
        # Skip validation if we've already validated through the API
        skip_validation = use_api_server and is_valid
        success, message = save_license_key(
            license_key, skip_validation=skip_validation
        )

        if success:
            # After saving, make a copy of the license to help diagnose any issues
            # This backup helps on systems where home directory permissions might cause issues
            try:
                import os

                backup_dir = os.path.join(
                    os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
                    ".license_backup",
                )
                os.makedirs(backup_dir, exist_ok=True)
                backup_path = os.path.join(backup_dir, "license_key.txt")
                with open(backup_path, "w") as f:
                    f.write(license_key)
                console.print(
                    "[green]License backup saved for diagnostic purposes[/green]"
                )
            except Exception as backup_error:
                # Backup is not critical, so just log the error
                console.print(
                    f"[yellow]Note: License backup failed: {str(backup_error)}[/yellow]"
                )
    except Exception as e:
        console.print(f"[red]Error saving license: {str(e)}[/red]")
        success = False
        message = f"License validation succeeded but saving failed: {str(e)}"

    if success:
        # Clear any cached credentials to force refresh
        clear_api_cache()

        # Display license details
        license_info = result
        expiration_date = datetime.datetime.fromisoformat(license_info["expires_at"])
        formatted_date = expiration_date.strftime("%B %d, %Y")
        customer = license_info.get("customer", "")
        email = license_info.get("email", "")

        # Create a table with license details
        table = Table(box=None)
        table.add_column("Property", style="cyan")
        table.add_column("Value", style="green")

        table.add_row("Customer", customer)
        table.add_row("Email", email)
        table.add_row("Expires On", formatted_date)
        if use_api_server and creds_success:
            table.add_row("Decryption Mode", "[green]API Server[/green]")
        else:
            table.add_row("Decryption Mode", "[yellow]Local[/yellow]")

        console.print(
            Panel(
                Markdown("✅ **License Activated Successfully!**\n"),
                border_style="green",
                title="License Activated",
                title_align="left",
                padding=(1, 2),
            )
        )
    else:
        console.print(
            Panel(
                Markdown(f"❌ **Error**: {message}"),
                border_style="red",
                title="License Activation Failed",
                title_align="left",
                padding=(1, 2),
            )
        )


def reset_license_command():
    """Reset (remove) the current license"""
    # First clear the API cache
    clear_api_cache()

    # Then remove the license file
    success, message = remove_license_key()

    if success:
        console.print(
            Panel(
                Markdown(
                    "✅ **License removed successfully!**\n\nAll credentials have been cleared. You'll need to add a new license to use FRIDAY AI CLI."
                ),
                border_style="yellow",
                title="License Reset",
                title_align="left",
                padding=(1, 2),
            )
        )
    else:
        console.print(
            Panel(
                Markdown(f"ℹ️ {message}"),
                border_style="yellow",
                title="License Status",
                title_align="left",
                padding=(1, 2),
            )
        )


def check_license_on_startup():
    """Check license validity on startup and prompt if needed"""
    status = get_license_status()

    if status["status"] == "unlicensed":
        console.print(
            Panel(
                Markdown(
                    "⚠️ **No license key found**\n\n"
                    "FRIDAY AI CLI requires a valid license to operate.\n"
                    "Please use `friday add-license <YOUR_LICENSE_KEY>` to activate."
                ),
                border_style="yellow",
                title="License Required",
                title_align="left",
                padding=(1, 2),
            )
        )
        return False
    elif status["status"] == "invalid":
        console.print(
            Panel(
                Markdown(
                    f"❌ **License Error**: {status['message']}\n\n"
                    "Please use `friday add-license <YOUR_LICENSE_KEY>` to update your license."
                ),
                border_style="red",
                title="Invalid License",
                title_align="left",
                padding=(1, 2),
            )
        )
        return False
    elif status["status"] == "licensed":
        # Try to validate license with the server if possible
        license_key = get_saved_license_key()
        if license_key and os.getenv("FRIDAY_USE_API_SERVER", "true").lower() == "true":
            # First check if we already have secure credentials
            has_secure_creds = False
            try:
                from .api_client import load_secure_credentials

                secure_creds = load_secure_credentials()
                has_secure_creds = bool(
                    secure_creds
                    and "encryption_key" in secure_creds
                    and "encryption_salt" in secure_creds
                )
                if has_secure_creds:
                    console.print("[green]Using securely stored credentials[/green]")
            except Exception:
                pass

            # Only contact server if we don't have secure credentials
            if not has_secure_creds:
                with console.status("Checking license with server..."):
                    try:
                        # Try to silently validate with the server and get credentials
                        success, creds_result = get_decryption_credentials(license_key)
                        if success:
                            if (
                                "encryption_key" in creds_result
                                and "encryption_salt" in creds_result
                            ):
                                console.print(
                                    "[green]Successfully retrieved decryption keys from server[/green]"
                                )

                                # Save them securely
                                try:
                                    from .api_client import save_secure_credentials

                                    save_secure_credentials(creds_result)
                                    
                                    # Attempt to manually decrypt modules
                                    try:
                                        from .crypto import decrypt_all_modules
                                        with console.status("Decrypting core modules..."):
                                            success, decrypt_result = decrypt_all_modules()
                                        
                                        if success:
                                            stats = decrypt_result.get("statistics", {})
                                            decrypted = stats.get("decrypted", 0)
                                            console.print(f"[green]Successfully decrypted {decrypted} core modules[/green]")
                                        else:
                                            error = decrypt_result.get("error", "Unknown error during decryption")
                                            console.print(f"[yellow]Warning: {error}[/yellow]")
                                            console.print("[yellow]Using fallback import hook mechanism[/yellow]")
                                    except Exception as decrypt_err:
                                        console.print(f"[yellow]Warning: Could not decrypt modules: {str(decrypt_err)}[/yellow]")
                                        console.print("[yellow]Using fallback import hook mechanism[/yellow]")
                                    console.print(
                                        "[dim]Credentials saved securely for offline use[/dim]"
                                    )
                                except Exception as e:
                                    console.print(
                                        f"[yellow]Note: Could not save credentials: {e}[/yellow]"
                                    )
                            else:
                                console.print(
                                    "[yellow]Warning: Server response missing encryption keys[/yellow]"
                                )
                        else:
                            console.print(
                                "[yellow]Warning: Could not communicate with the license server. "
                                "Using local validation.[/yellow]"
                            )
                    except Exception as e:
                        # Log but continue if server is unavailable
                        console.print(
                            f"[yellow]Warning: Server error: {str(e)}. Using local validation.[/yellow]"
                        )

        if status["expires_in_days"] < 30:
            # Show warning if license expires soon
            console.print(
                Panel(
                    Markdown(
                        f"⚠️ **License Expiring Soon**\n\n"
                        f"Your license will expire in {status['expires_in_days']} days.\n"
                        f"Please contact support to renew your license."
                    ),
                    border_style="yellow",
                    title="License Warning",
                    title_align="left",
                    padding=(1, 2),
                )
            )
        return True

    return False


def show_license_info():
    """Display information about the current license"""
    # First check if license file exists, before validation
    from .manager import get_license_file_path

    license_file = get_license_file_path()
    if license_file.exists():
        # Show raw license key for debugging
        try:
            license_key = license_file.read_text().strip()
            # Show just the first 20 chars to avoid filling the screen
            preview = license_key[:20] + "..." if len(license_key) > 20 else license_key
            console.print(f"[dim]License key: {preview}[/dim]")
        except Exception as e:
            console.print(f"[yellow]Error reading license file: {e}[/yellow]")

    # Get license status (includes validation)
    status = get_license_status()

    if status["status"] == "unlicensed":
        console.print(
            Panel(
                Markdown("⚠️ No license key found"),
                border_style="yellow",
                title="License Status",
                title_align="left",
                padding=(1, 2),
            )
        )
    elif status["status"] == "invalid":
        # Provide more detailed error message
        error_msg = status.get("message", "Unknown error")

        # Check if we have a backup license for comparison
        try:
            backup_path = os.path.join(
                os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
                ".license_backup",
                "license_key.txt",
            )
            if os.path.exists(backup_path):
                with open(backup_path, "r") as f:
                    backup_key = f.read().strip()
                if backup_key:
                    preview = (
                        backup_key[:20] + "..." if len(backup_key) > 20 else backup_key
                    )
                    console.print(f"[dim]Backup license found: {preview}[/dim]")
        except Exception:
            pass

        console.print(
            Panel(
                Markdown(f"❌ **Invalid License**: {error_msg}"),
                border_style="red",
                title="License Status",
                title_align="left",
                padding=(1, 2),
            )
        )
    elif status["status"] == "licensed":
        # Try to check mode - API or local
        license_key = get_saved_license_key()
        decryption_mode = "Local"

        if license_key:
            try:
                # Check if API credentials work
                success, _ = get_decryption_credentials(license_key)
                if success:
                    decryption_mode = "API Server"
            except Exception:
                # Silently fail if server is unavailable
                pass

        expiration_date = datetime.datetime.fromtimestamp(status["data"]["expire_at"])
        formatted_date = expiration_date.strftime("%B %d, %Y")

        # Create a table with license details
        table = Table(box=None)
        table.add_column("Property", style="cyan")
        table.add_column("Value", style="green")

        table.add_row("Customer", status["name"])
        table.add_row("Email", status["customer"])
        table.add_row(
            "Expires On",
            f"{formatted_date} ({status['expires_in_days']} days remaining)",
        )
        table.add_row("License Version", status["data"]["version"])
        table.add_row(
            "Decryption Mode",
            f"{'[green]' if decryption_mode == 'API Server' else '[yellow]'}{decryption_mode}[/]",
        )

        console.print(
            Panel(
                table,
                border_style="green",
                title="License Status",
                title_align="left",
                padding=(1, 2),
            )
        )
