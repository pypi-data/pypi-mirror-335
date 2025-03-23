import os
import json
import base64
import hashlib
import time
from pathlib import Path
from typing import Dict, Optional, Tuple, Union, Any
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from .api_client import validate_license
import dotenv

# Load environment variables
dotenv.load_dotenv()

# Constants
LICENSE_VERSION = "1.0"
KEY_ITERATIONS = 100000  # Number of iterations for key derivation
LICENSE_FILE_NAME = ".friday_license"

# Get environment variables
LICENSE_SALT = os.getenv("FRIDAY_LICENSE_SALT", "friday_default_salt")
LICENSE_SECRET = os.getenv("FRIDAY_LICENSE_SECRET", "friday_default_secret")


def get_license_file_path() -> Path:
    """Returns the path to the license file in the user's home directory"""
    home_dir = Path.home()
    return home_dir / LICENSE_FILE_NAME


def derive_key(secret: str, salt: str) -> bytes:
    """Derive a key from the secret and salt"""
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt.encode(),
        iterations=KEY_ITERATIONS,
    )
    return base64.urlsafe_b64encode(kdf.derive(secret.encode()))


def validate_license_key(license_key: str) -> Tuple[bool, Dict[str, Any]]:
    """Validate a license key

    Args:
        license_key: The license key to validate

    Returns:
        A tuple with (is_valid, license_data)
    """
    try:
        # Decode from base64
        encrypted_data = base64.urlsafe_b64decode(license_key)

        # Decrypt
        key = derive_key(LICENSE_SECRET, LICENSE_SALT)
        fernet = Fernet(key)
        decrypted_data = fernet.decrypt(encrypted_data).decode()

        # Parse JSON
        license_data = json.loads(decrypted_data)

        # Verify checksum
        checksum = license_data.pop("checksum", None)
        if not checksum:
            return False, {"error": "Invalid license: missing checksum"}

        checksum_data = f"{license_data['version']}:{license_data['customer_id']}:{license_data['name']}:{license_data['created_at']}:{license_data['expire_at']}"
        computed_checksum = hashlib.sha256(checksum_data.encode()).hexdigest()[:16]

        if checksum != computed_checksum:
            return False, {"error": "Invalid license: checksum verification failed"}

        # Check expiration
        current_time = int(time.time())
        if license_data["expire_at"] < current_time:
            return False, {"error": "License has expired", "data": license_data}

        # Add checksum back to data
        license_data["checksum"] = checksum

        return True, {"data": license_data}

    except Exception as e:
        return False, {"error": f"License validation error: {str(e)}"}


def save_license_key(
    license_key: str, skip_validation: bool = False
) -> Tuple[bool, str]:
    """Save a license key to the user's home directory

    Args:
        license_key: The license key to save
        skip_validation: If True, skips the local validation (useful when already validated by API)

    Returns:
        A tuple with (success, message)
    """
    # Validate the license first (unless asked to skip)
    if not skip_validation:
        is_valid, result = validate_license_key(license_key)
        if not is_valid:
            return False, result.get("error", "Invalid license key")

    try:
        license_file = get_license_file_path()
        license_file.write_text(license_key)
        return True, "License saved successfully"
    except Exception as e:
        return False, f"Failed to save license: {str(e)}"


def get_saved_license_key() -> Optional[str]:
    """Get the saved license key if it exists

    Returns:
        The license key string or None if not found
    """
    license_file = get_license_file_path()
    if license_file.exists():
        try:
            return license_file.read_text().strip()
        except Exception:
            return None
    return None


def remove_license_key() -> Tuple[bool, str]:
    """Remove the saved license key

    Returns:
        A tuple with (success, message)
    """
    license_file = get_license_file_path()
    if license_file.exists():
        try:
            license_file.unlink()
            return True, "License removed successfully"
        except Exception as e:
            return False, f"Failed to remove license: {str(e)}"
    return False, "No license found"


def get_license_status() -> Dict[str, Any]:
    """Get the current license status

    Returns:
        A dictionary with license status information
    """
    license_key = get_saved_license_key()
    if not license_key:
        return {"status": "unlicensed", "message": "No license key found"}

    is_valid, api_result = validate_license(license_key)
    if is_valid and api_result.get("status") == "valid":
        # Convert API response to match our expected format
        # Typically contains: customer, email, expires_at, valid_until, license_version
        days_remaining = 365  # Default value
        try:
            from datetime import datetime
            import time

            expire_date = datetime.fromisoformat(api_result["expires_at"])
            expire_timestamp = int(expire_date.timestamp())
            days_remaining = (expire_timestamp - int(time.time())) // 86400
        except Exception:
            pass  # Use default if conversion fails

        # Create a compatible response structure
        return {
            "status": "licensed",
            "customer": api_result.get("email", ""),
            "name": api_result.get("customer", ""),
            "expires_in_days": days_remaining,
            "data": {
                "customer_id": api_result.get("email", ""),
                "name": api_result.get("customer", ""),
                "expire_at": (
                    expire_timestamp
                    if "expire_timestamp" in locals()
                    else (int(time.time()) + 86400 * days_remaining)
                ),
                "version": api_result.get("license_version", "1.0"),
            },
        }
