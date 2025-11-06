"""Parameter resolution utilities for rig modules.

This module provides helper functions to resolve parameter values from both
modern keyword arguments and legacy positional/keyword argument patterns.
This enables backward compatibility while transitioning to cleaner APIs.

The functions support:
- Required parameters with validation
- Optional parameters with defaults
- Legacy argument name mappings
- Automatic keyword argument consumption to detect unused parameters
"""

from __future__ import annotations

from typing import Any

__all__ = ["resolve_required", "resolve_optional"]


def resolve_required(
    value: Any,
    legacy_kwargs: dict[str, Any],
    legacy_keys: tuple[str, ...],
    label: str,
) -> Any:
    """Resolve a required parameter supporting legacy keyword arguments.

    This function checks if a parameter value was provided using the modern
    argument name. If not, it checks for legacy argument names. If still not
    found, it raises a ValueError.

    Args:
        value: The value from the modern keyword argument (may be None).
        legacy_kwargs: Dictionary of legacy keyword arguments to check and consume.
        legacy_keys: Tuple of legacy argument names to check (in priority order).
        label: Human-readable parameter name for error messages.

    Returns:
        The resolved parameter value from either modern or legacy sources.

    Raises:
        ValueError: If the parameter is not provided via any supported name.

    Example:
        >>> legacy_kwargs = {'oldName': 'value1'}
        >>> result = resolve_required(None, legacy_kwargs, ('oldName',), 'new_name')
        >>> result
        'value1'
        >>> legacy_kwargs
        {}

        >>> resolve_required(None, {}, ('oldName',), 'new_name')
        Traceback (most recent call last):
        ...
        ValueError: new_name is required.
    """
    if value is not None:
        return value
    for key in legacy_keys:
        if key in legacy_kwargs:
            return legacy_kwargs.pop(key)
    raise ValueError(f"{label} is required.")


def resolve_optional(
    value: Any,
    legacy_kwargs: dict[str, Any],
    legacy_keys: tuple[str, ...],
    default: Any,
) -> Any:
    """Resolve an optional parameter supporting legacy keyword arguments.

    This function checks if a parameter value was provided using the modern
    argument name. If not, it checks for legacy argument names. If still not
    found, it returns the default value.

    Args:
        value: The value from the modern keyword argument (may be None).
        legacy_kwargs: Dictionary of legacy keyword arguments to check and consume.
        legacy_keys: Tuple of legacy argument names to check (in priority order).
        default: Default value to return if parameter not found.

    Returns:
        The resolved parameter value from modern args, legacy args, or default.

    Example:
        >>> legacy_kwargs = {'oldName': 'value1'}
        >>> result = resolve_optional(None, legacy_kwargs, ('oldName',), 'default')
        >>> result
        'value1'
        >>> legacy_kwargs
        {}

        >>> resolve_optional(None, {}, ('oldName',), 'default')
        'default'

        >>> resolve_optional('modern_value', {'oldName': 'old'}, ('oldName',), 'default')
        'modern_value'
    """
    if value is not None:
        return value
    for key in legacy_keys:
        if key in legacy_kwargs:
            return legacy_kwargs.pop(key)
    return default


if __name__ == "__main__":
    import doctest

    doctest.testmod()
