"""Helpers for working with rig naming conventions."""

from __future__ import annotations

__all__ = ['remove_suffix', 'get_side', 'get_alpha']


def remove_suffix(name: str) -> str:
    """Return ``name`` without its trailing underscore-delimited suffix."""
    parts = name.split('_')
    if len(parts) < 2:
        return name
    suffix = '_' + parts[-1]
    return name[: -len(suffix)]


def get_side(name: str) -> str:
    """Return the side prefix (e.g. ``'l_'``) from a rig name if present."""
    parts = name.split('_')
    if len(parts) < 3:
        return ''
    return parts[0] + '_'


def get_alpha(index: int) -> str:
    """Return the alphabet character for ``index`` (0=A, 25=Z)."""
    if 0 <= index <= 25:
        return chr(65 + index)
    return ''
