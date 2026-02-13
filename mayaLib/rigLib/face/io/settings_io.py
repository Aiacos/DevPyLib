"""Settings I/O operations for facial rigging data.

This module provides functions for saving and loading facial rig settings
to/from JSON files. It handles the serialization of all facial rig
configuration parameters including geometry selections, skin settings,
and joint optimization options.
"""

import json
import logging
import os

__author__ = "Lorenzo Argentieri"

logger = logging.getLogger(__name__)


# Default settings structure with all expected keys
DEFAULT_SETTINGS = {
    # Geometry selections
    "LHeadGeoSel": "",
    "REyeGeoSel": "",
    "LEyeGeoSel": "",
    "TopTeethGeoSel": "",
    "DownTeethGeoSel": "",
    "TongueGeoSel": "",
    "ExtraGeoSel": "",
    # Prefix and suffix options
    "chkPrefix": False,
    "skinJntSuffix": "_skn",
    # Bind skin options
    "chkMaintainMaxInf": True,
    "maxInfs": 12,
    "relaxSk": 2,
    # Deformation layer options
    "chkGame": False,
    "chkSoftMod": False,
    "chkTweaker": False,
    # Joint optimization options
    "chkOptLip": True,
    "lipJnt": 20,
    "chkOptEyelidJnt": False,
    "eyelidJnt": 20,
    "chkOptEye": True,
    "eyeCreaseJnt": 8,
    # Extra geometry checkbox
    "chkExtra": 0,
}


def save_settings(settings_dict: dict, filepath: str) -> bool:
    """Save facial rig settings dictionary to a JSON file.

    Writes the provided settings dictionary to a JSON file with
    pretty formatting for human readability.

    Args:
        settings_dict: Dictionary containing facial rig settings.
            Should contain geometry selections, skin options,
            and joint optimization parameters.
        filepath: Path to the output JSON file. Should end with '.json'.

    Returns:
        True if save was successful, False otherwise.

    Raises:
        OSError: If the file cannot be written.
        TypeError: If settings_dict contains non-serializable objects.

    Example:
        >>> settings = {"LHeadGeoSel": "head_geo", "maxInfs": 12}
        >>> save_settings(settings, "/path/to/facial_settings.json")
        True
    """
    try:
        # Ensure directory exists
        dir_path = os.path.dirname(filepath)
        if dir_path and not os.path.exists(dir_path):
            os.makedirs(dir_path)

        with open(filepath, "w", encoding="utf-8") as fp:
            json.dump(
                settings_dict,
                fp,
                sort_keys=True,
                indent=4,
                ensure_ascii=False,
            )
        logger.info("Facial settings saved to: %s", filepath)
        return True

    except (OSError, TypeError) as e:
        logger.error("Failed to save settings to %s: %s", filepath, e)
        raise


def load_settings(filepath: str) -> dict:
    """Load facial rig settings from a JSON file.

    Reads and parses a JSON file containing facial rig settings.
    The file should have been created by save_settings() or follow
    the same format.

    Args:
        filepath: Path to the JSON file to load.

    Returns:
        Dictionary containing the loaded facial rig settings.

    Raises:
        FileNotFoundError: If the specified file does not exist.
        json.JSONDecodeError: If the file contains invalid JSON.
        OSError: If the file cannot be read.

    Example:
        >>> settings = load_settings("/path/to/facial_settings.json")
        >>> print(settings["LHeadGeoSel"])
        'head_geo'
    """
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"Settings file not found: {filepath}")

    try:
        with open(filepath, encoding="utf-8") as fp:
            data = json.load(fp)
        logger.info("Facial settings loaded from: %s", filepath)
        return data

    except json.JSONDecodeError as e:
        logger.error("Invalid JSON in settings file %s: %s", filepath, e)
        raise
    except OSError as e:
        logger.error("Failed to read settings file %s: %s", filepath, e)
        raise


def get_default_settings() -> dict:
    """Get a copy of the default facial rig settings.

    Returns a dictionary with all settings initialized to their
    default values. This can be used to reset settings or as
    a template for new configurations.

    Returns:
        Dictionary containing default facial rig settings.

    Example:
        >>> defaults = get_default_settings()
        >>> print(defaults["maxInfs"])
        12
    """
    return DEFAULT_SETTINGS.copy()


def validate_settings(settings_dict: dict) -> tuple[bool, list[str]]:
    """Validate a settings dictionary for required keys and types.

    Checks that the provided settings dictionary contains all
    required keys and that values are of the expected types.

    Args:
        settings_dict: Dictionary to validate.

    Returns:
        Tuple of (is_valid, errors) where is_valid is True if
        validation passed, and errors is a list of error messages.

    Example:
        >>> is_valid, errors = validate_settings({"LHeadGeoSel": "head"})
        >>> print(is_valid)
        True
    """
    errors = []

    # Check for required keys
    required_keys = ["LHeadGeoSel"]
    for key in required_keys:
        if key not in settings_dict:
            errors.append(f"Missing required key: {key}")

    # Validate numeric values if present
    numeric_keys = ["maxInfs", "relaxSk", "lipJnt", "eyelidJnt", "eyeCreaseJnt"]
    for key in numeric_keys:
        if key in settings_dict:
            value = settings_dict[key]
            if not isinstance(value, (int, float)):
                errors.append(f"Key '{key}' must be numeric, got {type(value).__name__}")
            elif value < 0:
                errors.append(f"Key '{key}' must be non-negative, got {value}")

    # Validate boolean values if present
    bool_keys = [
        "chkMaintainMaxInf",
        "chkGame",
        "chkSoftMod",
        "chkTweaker",
        "chkOptLip",
        "chkOptEyelidJnt",
        "chkOptEye",
        "chkPrefix",
    ]
    for key in bool_keys:
        if key in settings_dict:
            value = settings_dict[key]
            if not isinstance(value, (bool, int)):
                errors.append(f"Key '{key}' must be boolean, got {type(value).__name__}")

    return len(errors) == 0, errors


def merge_with_defaults(settings_dict: dict) -> dict:
    """Merge provided settings with defaults for missing values.

    Takes a partial settings dictionary and fills in any missing
    keys with their default values.

    Args:
        settings_dict: Partial settings dictionary.

    Returns:
        Complete settings dictionary with defaults for missing keys.

    Example:
        >>> partial = {"LHeadGeoSel": "head_geo"}
        >>> full = merge_with_defaults(partial)
        >>> print(full["maxInfs"])
        12
    """
    result = get_default_settings()
    result.update(settings_dict)
    return result


def get_associated_curve_path(json_filepath: str) -> str:
    """Get the associated Maya curve file path for a settings JSON.

    Facial settings JSON files are typically paired with a Maya ASCII
    file containing curve and locator data. This function returns the
    expected path of that curve file.

    Args:
        json_filepath: Path to the settings JSON file.

    Returns:
        Path to the associated Maya ASCII curve file.

    Example:
        >>> curve_path = get_associated_curve_path("/path/to/settings.json")
        >>> print(curve_path)
        '/path/to/settings.ma'
    """
    return json_filepath.replace(".json", ".ma")


def to_json(dictionary: dict, filename: str) -> None:
    """Write dictionary to JSON file (legacy compatibility function).

    This function provides backward compatibility with the original
    facial3.py to_json method.

    Deprecated:
        Use save_settings() instead for better error handling.

    Args:
        dictionary: Dictionary to serialize.
        filename: Output file path.
    """
    save_settings(dictionary, filename)


# Module-level exports
__all__ = [
    "DEFAULT_SETTINGS",
    "save_settings",
    "load_settings",
    "get_default_settings",
    "validate_settings",
    "merge_with_defaults",
    "get_associated_curve_path",
    "to_json",
]
