import os
import sys
import importlib.abc
import importlib.machinery
import importlib.util
import marshal
import types
import logging
from pathlib import Path
from typing import Dict, Optional, Tuple, Set
from cryptography.fernet import Fernet

# Configure logging with minimal output for users
logging.basicConfig(level=logging.ERROR)
logger = logging.getLogger("friday-crypto")

from .manager import get_saved_license_key, derive_key
from .api_client import get_decryption_credentials

# Environment variables (default values, will be overridden by API credentials)
ENCRYPTION_KEY = os.getenv("FRIDAY_ENCRYPTION_KEY", "friday_default_encryption_key")
ENCRYPTION_SALT = os.getenv("FRIDAY_ENCRYPTION_SALT", "friday_default_encryption_salt")

# Server connection settings
USE_API_SERVER = os.getenv("FRIDAY_USE_API_SERVER", "true").lower() == "true"
API_FALLBACK_TO_LOCAL = (
    os.getenv("FRIDAY_API_FALLBACK_TO_LOCAL", "true").lower() == "true"
)

# Marker for encrypted modules
ENCRYPTED_MARKER = b"#FRIDAY-ENCRYPTED#"

# Cache for decrypted modules - stores compiled bytecode for efficiency
_DECRYPTED_CACHE: Dict[str, bytes] = {}

# Cache for decrypted source - stores the actual decrypted source code
_DECRYPTED_SOURCE_CACHE: Dict[str, bytes] = {}

# Cached decryption credentials
_CACHED_CREDENTIALS: Dict[str, str] = {}

# Flag to indicate if memory-only mode is active
MEMORY_ONLY_MODE = True

# List of modules that can be imported without a license
# These are essential for the license management commands to work
LICENSE_FREE_MODULES = {
    "friday.license",
    "friday.license.manager",
    "friday.license.cli",
    "friday.license.crypto",
    "friday.main",  # Main module needs to be accessible for CLI commands
    "friday.ui.welcome",  # UI components for basic functionality
    "friday.ui.terminal",
}


def encrypt_source(source_code: bytes) -> bytes:
    """
    Encrypt Python source code (plain text) and return encrypted data with marker.
    This updated version encrypts the source directly so it can be decrypted back to the original code.

    Args:
        source_code: The source code bytes to encrypt

    Returns:
        Encrypted bytes with marker prepended.
    """
    # Skip if already encrypted
    if source_code.startswith(ENCRYPTED_MARKER):
        return source_code

    # Ensure encryption credentials are set
    if not ENCRYPTION_KEY or not ENCRYPTION_SALT:
        raise ValueError(
            "Missing encryption environment variables. "
            "Please set FRIDAY_ENCRYPTION_KEY and FRIDAY_ENCRYPTION_SALT in your .env file."
        )

    try:
        key = derive_key(ENCRYPTION_KEY, ENCRYPTION_SALT)
        fernet = Fernet(key)
        encrypted_data = fernet.encrypt(source_code)  # Encrypt the plain text directly
        result = ENCRYPTED_MARKER + encrypted_data

        if not result.startswith(ENCRYPTED_MARKER):
            raise ValueError("Marker not added correctly during encryption")
        return result
    except Exception as e:
        raise ValueError(f"Encryption failed: {str(e)}")


def encrypt_directory(
    directory: Path, include_pattern: str = "*.py", verbose: bool = False
) -> Tuple[int, int]:
    """Encrypt all Python files in a directory

    Args:
        directory: The directory to encrypt
        include_pattern: Pattern for files to include
        verbose: Whether to print verbose output

    Returns:
        Tuple of (files_encrypted, files_skipped)
    """
    encrypted_count = 0
    skipped_count = 0
    error_count = 0
    license_free_modules_paths = set()

    # Skip encryption for license-free modules
    for module in LICENSE_FREE_MODULES:
        parts = module.split(".")
        # Convert module names to file paths
        if module.startswith("friday."):
            parts = parts[1:]  # Remove 'friday' prefix for path
        path_parts = [*parts[:-1], f"{parts[-1]}.py"]
        rel_path = os.path.join(*path_parts) if path_parts else ""
        abs_path = os.path.join(directory.parent, rel_path) if rel_path else ""
        if abs_path:
            license_free_modules_paths.add(Path(abs_path))

    if verbose:
        print(f"Processing directory: {directory}")
        print(f"License-free modules: {license_free_modules_paths}")

    # Process all Python files in this directory
    for py_file in directory.glob(include_pattern):
        if not py_file.is_file():
            continue

        # Skip license-free modules
        if py_file in license_free_modules_paths or any(
            str(py_file).startswith(str(p)) for p in license_free_modules_paths
        ):
            if verbose:
                print(f"Skipping license-free module: {py_file}")
            skipped_count += 1
            continue

        try:
            with open(py_file, "rb") as f:
                content = f.read()

            # Skip if already encrypted
            if content.startswith(ENCRYPTED_MARKER):
                if verbose:
                    print(f"Skipping already encrypted file: {py_file}")
                skipped_count += 1
                continue

            # Encrypt the file
            try:
                encrypted_content = encrypt_source(content)

                # Write back to the same file
                with open(py_file, "wb") as f:
                    f.write(encrypted_content)

                # Verify encryption worked
                with open(py_file, "rb") as f:
                    new_content = f.read()

                if not new_content.startswith(ENCRYPTED_MARKER):
                    print(
                        f"\033[91mWarning: Encryption verification failed for {py_file}!\033[0m"
                    )
                    error_count += 1
                else:
                    if verbose:
                        print(f"Successfully encrypted: {py_file}")
                    encrypted_count += 1
            except Exception as e:
                print(f"\033[91mError encrypting {py_file}: {str(e)}\033[0m")
                error_count += 1
        except Exception as e:
            print(f"\033[91mError processing {py_file}: {str(e)}\033[0m")
            error_count += 1

    # Recursively process subdirectories
    for subdir in directory.iterdir():
        if subdir.is_dir() and not subdir.name.startswith("."):
            sub_encrypted, sub_skipped = encrypt_directory(
                subdir, include_pattern, verbose
            )
            encrypted_count += sub_encrypted
            skipped_count += sub_skipped

    if error_count > 0:
        print(
            f"\033[91mWarning: {error_count} errors occurred during encryption\033[0m"
        )

    return encrypted_count, skipped_count


def get_decryption_keys() -> Tuple[bool, Dict[str, str]]:
    """Get decryption keys from secure storage or API server

    Returns:
        Tuple of (success, keys_dict) where keys_dict contains encryption_key and encryption_salt
    """
    global _CACHED_CREDENTIALS

    # Priority 1: Use in-memory cache if available
    if (
        _CACHED_CREDENTIALS
        and "encryption_key" in _CACHED_CREDENTIALS
        and "encryption_salt" in _CACHED_CREDENTIALS
    ):
        logger.debug("Using in-memory cached decryption credentials")
        return True, _CACHED_CREDENTIALS

    # Get license key
    license_key = get_saved_license_key()
    if not license_key:
        logger.warning("No license key found")
        return False, {
            "error": "No license key found. Please add a license using 'friday add-license YOUR_LICENSE_KEY'"
        }

    # Priority 2: Get credentials from API server
    logger.info("No cached credentials found, contacting server")

    try:
        # Import here to avoid circular imports
        from .api_client import get_decryption_credentials

        success, creds_data = get_decryption_credentials(license_key)

        if success:
            # Make sure we have the required fields
            if "encryption_key" in creds_data and "encryption_salt" in creds_data:
                # Log what we're using (without showing the actual values)
                logger.info("Using server-provided decryption credentials")
                logger.info("License System Checks Done!")

                # Cache the credentials in memory
                _CACHED_CREDENTIALS = {
                    "encryption_key": creds_data["encryption_key"],
                    "encryption_salt": creds_data["encryption_salt"],
                }
                return True, _CACHED_CREDENTIALS
            else:
                logger.error("Server response missing required encryption keys")
                return False, {
                    "error": "Server response missing required encryption fields"
                }
        else:
            # If server credentials retrieval failed
            error_msg = creds_data.get(
                "error", "Failed to get decryption credentials from server"
            )
            logger.error(f"Server credential retrieval failed: {error_msg}")
            return False, {"error": f"Server error: {error_msg}"}
    except ImportError:
        logger.error("Could not import credential retrieval module")
        return False, {"error": "Internal error: API client not available"}
    except Exception as e:
        logger.error(f"Error retrieving credentials: {e}")
        return False, {"error": f"Failed to get credentials: {str(e)}"}


def decrypt_source(encrypted_data: bytes) -> Optional[bytes]:
    """Decrypt encrypted Python source code.

    Args:
        encrypted_data: The encrypted source code with marker

    Returns:
        Decrypted source code bytes (plain text) or None if decryption fails.
    """
    # Verify the marker is present
    if not encrypted_data.startswith(ENCRYPTED_MARKER):
        return None

    # Remove marker to obtain actual encrypted bytes
    encrypted_bytes = encrypted_data[len(ENCRYPTED_MARKER) :]

    # Retrieve decryption keys from secure storage or API
    success, keys_data = get_decryption_keys()
    if not success:
        return None

    try:
        # Extract the actual key and salt if they contain formatting from the API
        # (API may return them in format like 'key:hash' or 'salt:hash')
        encryption_key = keys_data["encryption_key"]
        encryption_salt = keys_data["encryption_salt"]

        # Use environment variables as a fallback (for debug_decrypt.py compatibility)
        env_key = os.environ.get("FRIDAY_ENCRYPTION_KEY", "")
        env_salt = os.environ.get("FRIDAY_ENCRYPTION_SALT", "")

        # Try multiple approaches to derive the key
        fernet_keys_to_try = []

        # 1. First try directly with the provided keys
        try:
            key1 = derive_key(encryption_key, encryption_salt)
            fernet_keys_to_try.append((key1, "API keys direct"))
        except Exception:
            pass

        # 2. Try with environment variables if available
        if env_key and env_salt:
            try:
                key2 = derive_key(env_key, env_salt)
                fernet_keys_to_try.append((key2, "Environment variables"))
            except Exception:
                pass

        # 3. Try with parts before the colon if keys contain colons
        if ":" in encryption_key:
            base_key = encryption_key.split(":")[0]
            try:
                # First try with original salt
                key3 = derive_key(base_key, encryption_salt)
                fernet_keys_to_try.append((key3, "Base key with full salt"))
            except Exception:
                pass

        if ":" in encryption_salt:
            base_salt = encryption_salt.split(":")[0]
            try:
                # Try with base salt and full key
                key4 = derive_key(encryption_key, base_salt)
                fernet_keys_to_try.append((key4, "Full key with base salt"))
            except Exception:
                pass

        if ":" in encryption_key and ":" in encryption_salt:
            try:
                # Try with both base key and base salt
                key5 = derive_key(base_key, base_salt)
                fernet_keys_to_try.append((key5, "Base key with base salt"))
            except Exception:
                pass

        # Try each key until one works
        success = False
        last_error = None

        for fernet_key, key_source in fernet_keys_to_try:
            try:
                fernet = Fernet(fernet_key)
                decrypted_source = fernet.decrypt(encrypted_bytes)
                success = True
                break
            except Exception as e:
                last_error = e

        if not success:
            raise last_error or Exception("All decryption methods failed")

        return decrypted_source

    except Exception:
        return None


class FridayEncryptionFinder(importlib.abc.MetaPathFinder):
    """Custom import finder for encrypted FRIDAY modules"""

    # Modules that should be loaded from encrypted files
    protected_packages: Set[str] = {"friday.core"}

    def find_spec(self, fullname, path, target=None):
        """Find the module spec for the requested module"""
        # Only handle modules in our package
        if not fullname.startswith("friday."):
            return None

        if path is None:
            path = sys.path

        for entry in path:
            parts = fullname.split(".")
            parts[-1] += ".py"
            rel_path = os.path.join(*parts)
            abs_path = os.path.join(entry, rel_path)

            if os.path.exists(abs_path):

                is_license_free = fullname in LICENSE_FREE_MODULES or any(
                    fullname.startswith(f"{module}.") for module in LICENSE_FREE_MODULES
                )

                is_protected = any(
                    fullname == pkg or fullname.startswith(f"{pkg}.")
                    for pkg in self.protected_packages
                )

                return importlib.machinery.ModuleSpec(
                    name=fullname,
                    loader=FridayEncryptionLoader(
                        fullname, abs_path, is_protected, is_license_free
                    ),
                    origin=abs_path,
                    is_package=False,
                )
        return None


class FridayEncryptionLoader(importlib.abc.Loader):
    """Custom module loader for encrypted FRIDAY modules"""

    def __init__(self, fullname, path, is_protected=False, is_license_free=False):
        self.fullname = fullname
        self.path = path
        self.is_protected = is_protected
        self.is_license_free = is_license_free

    def create_module(self, spec):
        return None  # Use default module creation

    def exec_module(self, module):

        # First check if we have a cached bytecode version (fastest)
        if self.path in _DECRYPTED_CACHE:
            bytecode = _DECRYPTED_CACHE[self.path]

        # Next check if we have cached source but not bytecode
        elif self.path in _DECRYPTED_SOURCE_CACHE:
            decrypted_source = _DECRYPTED_SOURCE_CACHE[self.path]
            try:
                code_obj = compile(decrypted_source, self.path, "exec")
                bytecode = marshal.dumps(code_obj)
                # Cache for future use
                _DECRYPTED_CACHE[self.path] = bytecode
            except Exception as e:
                raise ImportError(
                    f"Error compiling cached source for {self.fullname}: {str(e)}"
                )

        # If not cached at all, need to read and possibly decrypt
        else:
            try:
                with open(self.path, "rb") as f:
                    source = f.read()

                # Check if file is encrypted
                if source.startswith(ENCRYPTED_MARKER):

                    # Handle license-free modules differently
                    if self.is_license_free:

                        # Just decode without decryption for license-free modules
                        source_text = source[len(ENCRYPTED_MARKER) :].decode("utf8")
                        code_obj = compile(source_text, self.path, "exec")
                        bytecode = marshal.dumps(code_obj)
                    else:
                        # This is a protected module that needs decryption

                        decrypted = decrypt_source(source)

                        if decrypted is None:
                            # Decryption failed - likely license issues

                            print(
                                f"\033[93mLicense required for {self.fullname}\033[0m"
                            )
                            print(
                                "Please use 'friday add-license <YOUR_LICENSE_KEY>' to activate FRIDAY."
                            )

                            if self.is_protected:
                                # Critical module - raise error
                                raise ImportError(
                                    f"Cannot import {self.fullname}. This module requires a valid license.\n"
                                    "Please use 'friday add-license <YOUR_LICENSE_KEY>' to activate."
                                )
                            else:
                                # Non-critical module - show warning
                                code_obj = compile(
                                    b"print('License required for full functionality')\n",
                                    self.path,
                                    "exec",
                                )
                                bytecode = marshal.dumps(code_obj)
                        else:
                            # Successful decryption!

                            # Store in source cache for future use
                            _DECRYPTED_SOURCE_CACHE[self.path] = decrypted

                            # Compile to bytecode
                            source_text = decrypted.decode("utf8")
                            code_obj = compile(source_text, self.path, "exec")
                            bytecode = marshal.dumps(code_obj)
                else:
                    # File is not encrypted, compile normally

                    code_obj = compile(source, self.path, "exec")
                    bytecode = marshal.dumps(code_obj)

                # Cache the bytecode for future imports
                _DECRYPTED_CACHE[self.path] = bytecode

            except Exception as e:
                if self.is_license_free:
                    raise ImportError(
                        f"Error loading essential module {self.fullname}: {str(e)}"
                    )
                else:
                    raise ImportError(
                        f"Error importing {self.fullname}: {str(e)}\n"
                        "This may be due to a missing or invalid license."
                    )

        try:
            code_obj = marshal.loads(bytecode)
            exec(code_obj, module.__dict__)
        except Exception as e:
            raise ImportError(f"Error executing module {self.fullname}: {str(e)}")


def install_import_hook():
    """Install the import hook for encrypted modules

    Note: This method is kept for backwards compatibility but is no longer the primary
    decryption mechanism. Use decrypt_all_modules() instead for more reliable operation.
    """
    finder = FridayEncryptionFinder()
    sys.meta_path.insert(0, finder)


def decrypt_all_modules(base_dir=None, memory_only=True, preload_sys_modules=True):
    """Process all encrypted modules in the friday.core package

    This handles decryption of modules and optionally loads them directly into sys.modules.

    Args:
        base_dir: Optional base directory where modules are located.
                If None, will try to find the package directory.
        memory_only: Override the global MEMORY_ONLY_MODE setting.
                     If True, modules are only decrypted in memory.
                     If False, modules are written back to disk.
                     If None, uses the global MEMORY_ONLY_MODE setting.
        preload_sys_modules: If True (default), directly injects decrypted modules into sys.modules.
                             This makes imports work without any special hooks.

    Returns:
        tuple: (success, dict_with_results_or_error)
    """
    # Get the package directory if not provided
    if base_dir is None:
        try:
            # Find the directory where the package is installed
            import friday

            base_dir = os.path.dirname(
                os.path.dirname(os.path.abspath(friday.__file__))
            )
        except ImportError:
            # Fallback to current directory if friday can't be imported
            base_dir = os.path.dirname(
                os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            )

    # Determine if we're using memory-only mode
    use_memory_only = MEMORY_ONLY_MODE if memory_only is None else memory_only
    mode_str = "memory-only" if use_memory_only else "disk-write"

    # Get decryption keys
    success, keys_data = get_decryption_keys()
    if not success:
        error_msg = keys_data.get("error", "Failed to get decryption keys")
        print(f"\033[91m[ERROR] {error_msg}\033[0m")
        return False, {"error": error_msg}

    # Find the core directory
    core_dir = os.path.join(base_dir, "friday", "core")
    if not os.path.exists(core_dir):
        error_msg = f"Core directory not found at {core_dir}"
        print(f"\033[91m[ERROR] {error_msg}\033[0m")
        return False, {"error": error_msg}

    # Statistics
    processed_count = 0
    skipped_count = 0
    error_count = 0
    results = {"processed": [], "skipped": [], "errors": []}

    # Process all Python files in the core directory and subdirectories
    for root, _, files in os.walk(core_dir):
        for file in files:
            if not file.endswith(".py"):
                continue

            file_path = os.path.join(root, file)
            rel_path = os.path.relpath(file_path, base_dir)

            # Skip license-free modules
            module_name = (
                "friday." + os.path.splitext(rel_path.replace(os.path.sep, "."))[0]
            )
            if module_name in LICENSE_FREE_MODULES or any(
                module_name.startswith(f"{m}.") for m in LICENSE_FREE_MODULES
            ):
                skipped_count += 1
                results["skipped"].append(rel_path)
                continue

            try:
                # Read the file content
                with open(file_path, "rb") as f:
                    content = f.read()

                # Check if the file is encrypted
                if not content.startswith(ENCRYPTED_MARKER):
                    skipped_count += 1
                    results["skipped"].append(rel_path)
                    continue

                # Process for verification or decryption
                if use_memory_only:
                    # In memory-only mode, we just verify decryption but keep encrypted on disk
                    decrypted_content = decrypt_source(content)

                    if decrypted_content is None:
                        error_msg = f"Failed to decrypt {rel_path}"
                        print(f"\033[91m[ERROR] {error_msg}\033[0m")
                        error_count += 1
                        results["errors"].append(
                            {"file": rel_path, "error": "Decryption failed"}
                        )
                        continue

                    # In memory-only mode, we just cache the decrypted content
                    _DECRYPTED_SOURCE_CACHE[file_path] = decrypted_content

                    # Also precompile for efficiency
                    try:
                        code_obj = compile(decrypted_content, file_path, "exec")
                        _DECRYPTED_CACHE[file_path] = marshal.dumps(code_obj)
                    except Exception as compile_error:
                        print(
                            f"\033[93m[WARNING] Compilation error for {rel_path}: {str(compile_error)}\033[0m"
                        )

                    processed_count += 1
                    results["processed"].append(rel_path)

                else:
                    # Legacy mode: decrypt and write to disk
                    decrypted_content = decrypt_source(content)

                    if decrypted_content is None:
                        error_msg = f"Failed to decrypt {rel_path}"
                        print(f"\033[91m[ERROR] {error_msg}\033[0m")
                        error_count += 1
                        results["errors"].append(
                            {"file": rel_path, "error": "Decryption failed"}
                        )
                        continue

                    # Write the decrypted content back to the file
                    with open(file_path, "wb") as f:
                        f.write(decrypted_content)

                    processed_count += 1
                    results["processed"].append(rel_path)

            except Exception as e:
                error_msg = f"Error processing {rel_path}: {str(e)}"
                print(f"\033[91m[ERROR] {error_msg}\033[0m")
                error_count += 1
                results["errors"].append({"file": rel_path, "error": str(e)})

    # If we're in memory-only mode and requested to preload modules directly, inject them into sys.modules
    preloaded_modules = 0
    if use_memory_only and preload_sys_modules and processed_count > 0:

        # Build a map of all modules we've processed
        module_map = {}
        for rel_path in results["processed"]:
            # Convert path to module name
            module_path = rel_path.replace(os.path.sep, ".")
            if module_path.endswith(".py"):
                module_path = module_path[:-3]  # Remove .py extension
            if module_path.startswith("friday."):
                module_name = module_path
            else:
                module_name = f"friday.{module_path}"

            # Get the full path
            full_path = os.path.join(base_dir, rel_path)
            module_map[module_name] = full_path

        # PHASE 1: Create all modules and register them in sys.modules WITHOUT executing
        # This helps with circular imports by making all modules available before execution
        module_code_map = {}  # Store compiled code for phase 2

        # Create essential package structure first
        packages = {
            "friday": types.ModuleType("friday"),
            "friday.core": types.ModuleType("friday.core"),
            "friday.core.tools": types.ModuleType("friday.core.tools"),
        }

        # Add proper attributes to packages
        for name, pkg in packages.items():
            if name not in sys.modules:
                pkg.__path__ = [os.path.join(base_dir, *name.split("."))]
                pkg.__package__ = name.rpartition(".")[0] if "." in name else ""
                pkg.__name__ = name
                pkg.__builtins__ = __builtins__
                sys.modules[name] = pkg

        for module_name, full_path in module_map.items():
            try:
                if module_name in sys.modules:
                    # Skip if already exists

                    continue

                if full_path not in _DECRYPTED_SOURCE_CACHE:
                    # We don't have the decrypted source, skip it
                    print(
                        f"\033[93m[WARNING] Missing decrypted source for {module_name}, skipping\033[0m"
                    )
                    continue

                # Create a new empty module object
                module = types.ModuleType(module_name)
                module.__file__ = full_path
                module.__path__ = [os.path.dirname(full_path)]
                module.__package__ = module_name.rpartition(".")[0]
                module.__builtins__ = __builtins__

                # Register the module in sys.modules without executing its code
                sys.modules[module_name] = module

                # Create parent package modules if they don't exist
                parent_package = module_name.rpartition(".")[0]
                while parent_package and parent_package not in sys.modules:
                    parent = types.ModuleType(parent_package)
                    parent.__path__ = [os.path.dirname(os.path.dirname(full_path))]
                    parent.__package__ = parent_package.rpartition(".")[0]
                    sys.modules[parent_package] = parent
                    parent_package = parent_package.rpartition(".")[0]

                # Compile the module code but don't execute it yet
                module_source = _DECRYPTED_SOURCE_CACHE[full_path]
                module_code = compile(module_source, full_path, "exec")
                module_code_map[module_name] = module_code

                preloaded_modules += 1
            except Exception as e:
                print(
                    f"\033[91m[ERROR] Failed to register module {module_name}: {str(e)}\033[0m"
                )
                error_count += 1
                results["errors"].append(
                    {"file": module_name, "error": f"Registration error: {str(e)}"}
                )

        # PHASE 2: Execute all modules now that they're all registered

        # Determine a safe execution order - bottom-up is often better for dependencies
        execution_order = sorted(
            module_code_map.keys(), key=lambda m: m.count("."), reverse=True
        )

        # Prioritize base modules that others might depend on, then initialize modules
        base_modules = [m for m in execution_order if m.endswith(".base")]
        init_modules = [m for m in execution_order if m.endswith(".__init__")]
        regular_modules = [
            m
            for m in execution_order
            if not m.endswith(".base") and not m.endswith(".__init__")
        ]
        execution_order = base_modules + init_modules + regular_modules

        # Make sure we have the ToolResult in the tools package
        tools_package = sys.modules.get("friday.core.tools")
        if tools_package and "ToolResult" not in tools_package.__dict__:
            # Create a simple ToolResult class directly in the tools package namespace
            tools_package.__dict__["ToolResult"] = type(
                "ToolResult",
                (object,),
                {
                    "__slots__": ["value", "error", "type"],
                    "__init__": lambda self, value=None, error=None, type=None: setattr(
                        self, "value", value
                    )
                    or setattr(self, "error", error)
                    or setattr(self, "type", type)
                    or None,
                },
            )

        executed_modules = 0
        for module_name in execution_order:
            try:
                module = sys.modules[module_name]
                module_code = module_code_map[module_name]

                # Execute the module code in its own namespace
                exec(module_code, module.__dict__)
                executed_modules += 1
            except Exception as e:
                print(
                    f"\033[91m[ERROR] Failed to execute module {module_name}: {str(e)}\033[0m"
                )
                error_count += 1
                results["errors"].append(
                    {"file": module_name, "error": f"Execution error: {str(e)}"}
                )

    # Add executed modules count to statistics if applicable
    stats = {
        "processed": processed_count,
        "skipped": skipped_count,
        "errors": error_count,
        "preloaded": preloaded_modules,
    }
    if "executed_modules" in locals():
        stats["executed"] = executed_modules

    if error_count > 0:
        return False, {"statistics": stats, "details": results}

    return True, {"statistics": stats, "details": results}
