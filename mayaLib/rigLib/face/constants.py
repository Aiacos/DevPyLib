"""Constants for facial rigging system.

This module contains UI styling constants (colors, stylesheets) and
file format extensions used throughout the facial rigging framework.
"""

# File extensions for data serialization
FILE_EXT = ".data"
"""File extension for single object data files."""

PACK_EXT = ".list"
"""File extension for packed/batch data files."""


# UI Stylesheet colors
# These are Qt stylesheet strings used for widget styling

EDGE_COLOR = "background-color:rgb(255,102,51);color : black;"
"""Orange background color for edge-related buttons."""

SELECTION_COLOR = "background-color:rgb(0,254,102);color : black;"
"""Green background color for selection buttons."""

EDGE_INDEX_COLOR = "background-color:rgb(0,179,255);color : black;"
"""Blue background color for edge index buttons."""

DARK_COLOR_A = "background-color:rgb(70,70,70);color : white;"
"""Dark gray background (level A - lightest dark)."""

DARK_COLOR_B = "background-color:rgb(50,50,50);color : white;"
"""Dark gray background (level B - medium dark)."""

DARK_COLOR_C = "background-color:rgb(30,30,30);color : white;"
"""Dark gray background (level C - darkest)."""

DEFAULT_COLOR = "background-color:rgb(90,90,90);color : white;"
"""Default gray background color for standard widgets."""

PROGRESS_COLOR = "background-color:rgb(76,50,50);color : white;"
"""Brownish-red background color for progress/status labels."""

DEFINE_COLOR = "color : white;"
"""White text color only (no background)."""

DEFINE_COLOR_2 = "color : black;"
"""Black text color only (no background)."""


# Legacy name mappings for backward compatibility
# These map the original instance attribute names to the new module constants
LEGACY_COLOR_MAPPING = {
    "edgeColor": EDGE_COLOR,
    "slColor": SELECTION_COLOR,
    "edgeIndColor": EDGE_INDEX_COLOR,
    "darkColorA": DARK_COLOR_A,
    "darkColorB": DARK_COLOR_B,
    "darkColorC": DARK_COLOR_C,
    "defaultColor": DEFAULT_COLOR,
    "progressColor": PROGRESS_COLOR,
    "defineColor": DEFINE_COLOR,
    "defineColor2": DEFINE_COLOR_2,
}


# Color RGB tuples for programmatic use
class Colors:
    """Color constants as RGB tuples for programmatic manipulation.

    These can be used when Qt stylesheets are not appropriate,
    such as when setting Maya override colors programmatically.
    """

    EDGE = (255, 102, 51)
    """Orange color for edges."""

    SELECTION = (0, 254, 102)
    """Green color for selections."""

    EDGE_INDEX = (0, 179, 255)
    """Blue color for edge indices."""

    DARK_A = (70, 70, 70)
    """Dark gray level A."""

    DARK_B = (50, 50, 50)
    """Dark gray level B."""

    DARK_C = (30, 30, 30)
    """Dark gray level C."""

    DEFAULT = (90, 90, 90)
    """Default gray."""

    PROGRESS = (76, 50, 50)
    """Progress/status brownish-red."""

    WHITE = (255, 255, 255)
    """White."""

    BLACK = (0, 0, 0)
    """Black."""


# Maya override color indices used in the original code
class MayaOverrideColors:
    """Maya display layer override color indices.

    These correspond to Maya's internal color index system
    used for viewport display colors.
    """

    RED = 1
    """Red color index."""

    BLUE = 6
    """Blue color index."""

    DARK_BLUE = 15
    """Dark blue color index."""

    WHITE = 16
    """White color index."""

    YELLOW = 17
    """Yellow color index."""
