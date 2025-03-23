import os
import json
import time
import logging
from typing import Dict, Any, Optional, Tuple
from pathlib import Path
import requests
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import base64
from datetime import datetime
import tempfile

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("friday-license-client")

# Default API URL (can be overridden with environment variable)
DEFAULT_API_URL = "https://friday-ai.yashchouriya.com/api/v1"
API_URL = os.getenv("FRIDAY_API_URL", DEFAULT_API_URL)

# Cache file location
CACHE_DIR = os.path.join(str(Path.home()), ".friday")
CREDENTIALS_CACHE_FILE = os.path.join(CACHE_DIR, ".credentials")
SECURE_CREDENTIALS_FILE = os.path.join(CACHE_DIR, ".credentials")
TOKEN_CACHE_FILE = os.path.join(CACHE_DIR, ".token")

# Cache TTL in seconds
CACHE_TTL = 86400  # 1 day for general cache
CREDENTIALS_TTL = 604800  # 1 week for credentials


def ensure_cache_dir(secure=False):
    """Ensure the cache directory exists with appropriate permissions

    Args:
        secure: Whether to set secure permissions (0o700) on the directory
    """
    if not os.path.exists(CACHE_DIR):
        try:
            # Create directory with user read/write/execute permissions only (more secure)
            if secure:
                os.makedirs(CACHE_DIR, mode=0o700, exist_ok=True)
            else:
                os.makedirs(CACHE_DIR, exist_ok=True)

            # Set permissions even if directory already existed
            if secure and os.path.exists(CACHE_DIR):
                os.chmod(CACHE_DIR, 0o700)

        except Exception as e:
            logger.warning(
                f"Error creating cache directory with secure permissions: {e}"
            )
            # Fall back to standard mkdir
            os.makedirs(CACHE_DIR, exist_ok=True)


def load_cache(cache_file: str) -> Optional[Dict[str, Any]]:
    """Load data from cache file"""
    if not os.path.exists(cache_file):
        return None

    try:
        # Check if cache is expired
        if time.time() - os.path.getmtime(cache_file) > CACHE_TTL:
            logger.debug(f"Cache expired: {cache_file}")
            return None

        with open(cache_file, "r") as f:
            return json.load(f)
    except Exception as e:
        logger.warning(f"Error loading cache: {str(e)}")
        return None


def save_cache(cache_file: str, data: Dict[str, Any], secure=False):
    """Save data to cache file atomically.

    Args:
        cache_file: Path to the cache file.
        data: Data to save.
        secure: Whether to set secure permissions (0o600) on the file.
    """
    # Ensure the cache directory exists with appropriate permissions.
    ensure_cache_dir(secure=secure)
    cache_dir = os.path.dirname(cache_file)

    try:
        # Create a temporary file in the same directory.
        fd, tmp_path = tempfile.mkstemp(dir=cache_dir)
        try:
            # Write the data to the temporary file.
            with os.fdopen(fd, "w") as tmp_file:
                json.dump(data, tmp_file)
                tmp_file.flush()
                os.fsync(tmp_file.fileno())
        except Exception as inner_e:
            os.remove(tmp_path)
            logger.error(f"Error writing to temporary file {tmp_path}: {inner_e}")
            raise inner_e

        # Atomically replace the target file with the temporary file.
        os.replace(tmp_path, cache_file)
        logger.debug(f"Temporary file {tmp_path} renamed to {cache_file}")

        # Set file permissions to user read/write only if secure.
        if secure and os.path.exists(cache_file):
            try:
                os.chmod(cache_file, 0o600)
                logger.debug(f"File permissions for {cache_file} set to 0o600")
            except Exception as perm_error:
                logger.warning(
                    f"Error setting secure permissions on {cache_file}: {perm_error}"
                )
    except Exception as e:
        logger.warning(f"Error saving cache to {cache_file}: {e}")


def save_secure_credentials(creds_data: Dict[str, Any]) -> bool:
    """Save credentials securely with restricted permissions

    Args:
        creds_data: Credential data containing encryption_key and encryption_salt

    Returns:
        True if successful, False otherwise
    """
    if (
        not creds_data
        or "encryption_key" not in creds_data
        or "encryption_salt" not in creds_data
    ):
        logger.warning("Cannot save incomplete credentials")
        return False

    # Prepare data structure with expiration
    secure_data = {
        "encryption_key": creds_data["encryption_key"],
        "encryption_salt": creds_data["encryption_salt"],
        "saved_at": int(time.time()),
        "expires_at": int(time.time()) + CREDENTIALS_TTL,
    }

    # Add other useful fields if available
    for field in ["customer", "email", "expires_at", "license_version"]:
        if field in creds_data:
            secure_data[field] = creds_data[field]

    try:
        # Save with secure permissions
        save_cache(SECURE_CREDENTIALS_FILE, secure_data, secure=False)

        if not os.path.exists(SECURE_CREDENTIALS_FILE):
            logger.error("Secure credentials file not found")
            return False

        logger.info("Credentials saved securely")
        return True
    except Exception as e:
        logger.error(f"Failed to save secure credentials: {e}")
        return False


def load_secure_credentials() -> Optional[Dict[str, Any]]:
    """Load securely stored credentials if available and not expired

    Returns:
        Dictionary with encryption_key and encryption_salt or None if not available
    """
    try:
        # Check if file exists
        if not os.path.exists(SECURE_CREDENTIALS_FILE):
            logger.debug("No secure credentials file found")
            return None

        # Read the file
        with open(SECURE_CREDENTIALS_FILE, "r") as f:
            creds = json.load(f)

        # Check expiration if provided
        if "expires_at" in creds:
            expires_at = creds["expires_at"]
            exp_timestamp = None

            # If numeric, use directly as a Unix timestamp.
            if isinstance(expires_at, (int, float)):
                exp_timestamp = expires_at
            # If it's a string, check if it's a numeric string or ISO8601 datetime.
            elif isinstance(expires_at, str):
                if expires_at.isdigit():
                    exp_timestamp = float(expires_at)
                else:
                    try:
                        dt = datetime.fromisoformat(expires_at)
                        exp_timestamp = dt.timestamp()
                    except ValueError:
                        logger.error("Invalid date format for expires_at")
                        return None
            else:
                logger.error("Invalid type for expires_at")
                return None

            # Compare the expiration timestamp to the current time.
            if exp_timestamp < time.time():
                logger.info("Secure credentials have expired")
                return None

        # Check required fields
        if "encryption_key" not in creds or "encryption_salt" not in creds:
            logger.warning("Secure credentials file is missing required fields")
            return None

        logger.info("Loaded secure credentials")
        return {
            "encryption_key": creds["encryption_key"],
            "encryption_salt": creds["encryption_salt"],
        }
    except Exception as e:
        logger.warning(f"Error loading secure credentials[api_client]: {e}")
        return None


def clear_cache():
    """Clear all cached credentials and tokens"""
    try:
        files_to_remove = [
            CREDENTIALS_CACHE_FILE,
            TOKEN_CACHE_FILE,
            SECURE_CREDENTIALS_FILE,
        ]

        for file_path in files_to_remove:
            if os.path.exists(file_path):
                os.remove(file_path)
                logger.debug(f"Removed cache file: {file_path}")

        return True
    except Exception as e:
        logger.warning(f"Error clearing cache: {str(e)}")
        return False


def authenticate(license_key: str) -> Tuple[bool, Dict[str, Any]]:
    """Authenticate with the license server

    Args:
        license_key: The license key to authenticate with

    Returns:
        Tuple of (success, data) where data contains either the token or an error message
    """
    # Check for cached token
    cached_token = load_cache(TOKEN_CACHE_FILE)
    if cached_token and cached_token.get("license_key") == license_key:
        logger.debug("Using cached authentication token")
        return True, cached_token

    # Attempt to authenticate with the server
    try:
        response = requests.post(
            f"{API_URL}/authenticate",
            json={"license_key": license_key},
            headers={"Content-Type": "application/json"},
            timeout=10,
        )

        if response.status_code == 200:
            # Cache the successful response
            token_data = response.json()
            token_data["license_key"] = (
                license_key  # Store license key for cache validation
            )
            save_cache(TOKEN_CACHE_FILE, token_data)
            return True, token_data
        else:
            error_msg = response.json().get(
                "error", f"Authentication failed with status {response.status_code}"
            )
            return False, {"error": error_msg}

    except requests.RequestException as e:
        logger.error(f"Authentication request failed: {str(e)}")
        return False, {"error": f"Connection error: {str(e)}"}
    except Exception as e:
        logger.error(f"Authentication error: {str(e)}")
        return False, {"error": f"Error: {str(e)}"}


def get_decryption_credentials(license_key: str) -> Tuple[bool, Dict[str, Any]]:
    """Get decryption credentials from the license server or secure storage

    Args:
        license_key: The license key to use

    Returns:
        Tuple of (success, credentials) where credentials contains either the keys or an error message
    """
    # First try to load from secure credentials storage
    secure_creds = load_secure_credentials()
    if secure_creds:
        logger.debug("Using securely stored credentials")
        # Add license key to the credentials for compatibility
        secure_creds["license_key"] = license_key
        return True, secure_creds

    # Fall back to standard cache if secure storage isn't available
    cached_creds = load_cache(CREDENTIALS_CACHE_FILE)
    if cached_creds and cached_creds.get("license_key") == license_key:
        logger.debug("Using cached decryption credentials")
        # Also save to secure storage for next time
        save_secure_credentials(cached_creds)
        return True, cached_creds

    logger.info("No local credentials found, contacting server")

    # First authenticate to get a token
    auth_success, auth_data = authenticate(license_key)
    if not auth_success:
        return False, auth_data  # Return the error

    # Use the token to get decryption credentials
    try:
        access_token = auth_data.get("access_token")
        response = requests.get(
            f"{API_URL}/decrypt-credentials",
            headers={
                "Authorization": f"Bearer {access_token}",
                "Content-Type": "application/json",
            },
            timeout=10,
        )

        if response.status_code == 200:
            # Get credential data from response
            creds_data = response.json()
            creds_data["license_key"] = (
                license_key  # Store license key for cache validation
            )

            # Save to both caches
            save_cache(CREDENTIALS_CACHE_FILE, creds_data)  # Standard cache
            save_secure_credentials(creds_data)  # Secure storage

            logger.info("Successfully retrieved and saved credentials from server")
            return True, creds_data
        else:
            error_msg = response.json().get(
                "error", f"Failed to get credentials with status {response.status_code}"
            )
            return False, {"error": error_msg}

    except requests.RequestException as e:
        logger.error(f"Credentials request failed: {str(e)}")
        return False, {"error": f"Connection error: {str(e)}"}
    except Exception as e:
        logger.error(f"Error getting credentials: {str(e)}")
        return False, {"error": f"Error: {str(e)}"}


def validate_license(license_key: str) -> Tuple[bool, Dict[str, Any]]:
    """Validate a license key with the server without getting credentials

    Args:
        license_key: The license key to validate

    Returns:
        Tuple of (is_valid, data) where data contains license info or error message
    """
    try:
        response = requests.post(
            f"{API_URL}/validate",
            json={"license_key": license_key},
            headers={"Content-Type": "application/json"},
            timeout=10,
        )
        if response.status_code == 200:
            response_data = response.json()

            # Check if the response indicates valid license
            # The server may return "status":"valid" or just succeed with customer info
            has_customer = "customer" in response_data
            has_valid_status = response_data.get("status") == "valid"

            if has_valid_status or has_customer:
                # Make sure we include a status field if it wasn't in the response
                if not has_valid_status and has_customer:
                    response_data["status"] = "valid"

                return True, response_data
            else:
                error_msg = "License validation failed on server"
                logger.warning(f"License validation failed: {response_data}")
                return False, {"error": error_msg}
        else:
            error_msg = response.json().get(
                "error", f"Validation failed with status {response.status_code}"
            )
            return False, {"error": error_msg}

    except requests.RequestException as e:
        logger.error(f"Validation request failed: {str(e)}")
        return False, {"error": f"Connection error: {str(e)}"}
    except Exception as e:
        logger.error(f"Validation error: {str(e)}")
        return False, {"error": f"Error: {str(e)}"}


def derive_key(secret: str, salt: str) -> bytes:
    """Derive a key from the secret and salt using PBKDF2"""
    try:
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt.encode(),
            iterations=100000,
        )
        return base64.urlsafe_b64encode(kdf.derive(secret.encode()))
    except Exception as e:
        logger.error(f"Key derivation error: {str(e)}")
        return b""
