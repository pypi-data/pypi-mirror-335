"""Load environment variables from .env or .json files."""

# pylint: disable=broad-exception-caught

import inspect
import json
import os
import re
from pathlib import Path


def load_env(filename: str = ".env.local", path: str | Path | None = None) -> bool:
    """
    Load environment variables from a file in the specified format.

    Args:
        filename: The name of the file to load. If it ends with .json, it's treated as a JSON file.
                 Otherwise, it's treated as a .env file.
        path: The path to the directory containing the file. If None, uses the caller's directory.

    Returns:
        True if the file was loaded successfully, False otherwise.
    """
    if path is None:
        # Get the caller's file path (the script that called this function)
        frame = inspect.currentframe()
        if frame is None or frame.f_back is None:
            # Fallback to current directory if frame information is not available
            path = Path.cwd()
        else:
            caller_file = frame.f_back.f_code.co_filename
            path = Path(caller_file).parent

    env_path = Path(path) / filename

    try:
        print(f"Loading environment from: {env_path}")

        if filename.lower().endswith(".json"):
            return _load_json_env(env_path)
        return _load_dotenv(env_path)

    except FileNotFoundError:
        print(f"Environment file not found: {env_path}")
        return False
    except PermissionError:
        print(f"Permission denied when accessing: {env_path}")
        return False
    except Exception as e:
        print(f"Error loading environment from {env_path}: {str(e)}")
        return False


def _is_valid_env_var_name(name: str) -> bool:
    """
    Check if a string is a valid environment variable name.
    Environment variables typically follow stricter rules than Python identifiers.
    """
    return bool(re.match(r"^[a-zA-Z_][a-zA-Z0-9_]*$", name))


def _load_dotenv(file_path: Path) -> bool:
    """Load environment variables from a .env file."""
    with open(file_path, mode="r", encoding="utf-8") as f:
        for line_num, line in enumerate(f, 1):
            # Skip empty lines and comments
            line = line.strip()
            if not line or line.startswith("#"):
                continue

            # Find the first equals sign
            try:
                # Split on the first equals sign
                if "=" not in line:
                    print(
                        f"Warning: Invalid format on line {line_num}, expected KEY=VALUE, skipping"
                    )
                    continue

                key, value = line.split("=", 1)
                key = key.strip()

                # # Check for comments at the end of the line
                # if "#" in value:
                #     # This is a simple approach; doesn't handle cases where # is inside quoted strings
                #     value = value.split("#", 1)[0].strip()

                # Validate environment variable name
                if not _is_valid_env_var_name(key):
                    print(
                        f"Warning: Invalid environment variable name '{key}' on line {line_num}, skipping"
                    )
                    continue

                # Process value
                value = value.strip()

                # Remove surrounding quotes if present
                if (value.startswith('"') and value.endswith('"')) or (
                    value.startswith("'") and value.endswith("'")
                ):
                    value = value[1:-1]

                # Expand variables in the value
                value = os.path.expandvars(value)

                os.environ[key] = value

            except Exception as e:
                print(f"Warning: Error processing line {line_num}: {str(e)}, skipping")
                continue

    return True


def _load_json_env(file_path: Path) -> bool:
    """Load environment variables from a JSON file."""
    with open(file_path, mode="r", encoding="utf-8") as f:
        try:
            data = json.load(f)
        except json.JSONDecodeError as e:
            print(f"Error: Invalid JSON format in {file_path}: {str(e)}")
            return False

    if not isinstance(data, dict):
        print(f"Error: JSON root must be an object/dictionary in {file_path}")
        return False

    for key, value in data.items():
        if not isinstance(key, str):
            print(f"Warning: Skipping non-string key {key} in JSON")
            continue

        if not _is_valid_env_var_name(key):
            print(
                f"Warning: Invalid environment variable name '{key}' in JSON, skipping"
            )
            continue

        # Convert value to appropriate string representation
        if isinstance(value, (list, dict)):
            # Use json.dumps for complex types
            os.environ[key] = json.dumps(value)
        else:
            # Use str() for primitives
            os.environ[key] = str(value)

    return True
