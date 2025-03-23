# License management module for FRIDAY CLI
# This module handles license creation, validation, and storage

from .manager import (
    validate_license_key,
    save_license_key,
    get_saved_license_key,
    remove_license_key,
)
