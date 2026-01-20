"""Luna Config launcher for mayaLib.

Provides a launcher function for the Luna configuration editor.
"""


def launch_configer():
    """Launch the Luna configuration editor.

    Opens the Luna Config window for managing Luna settings including:
    - Naming convention templates
    - Control shape library paths
    - Default component settings
    - Workspace preferences

    Returns:
        None: Opens the config window.

    Example:
        >>> launch_configer()

    """
    import luna
    from luna.interface.commands import tool_cmds

    tool_cmds.open_configer()
