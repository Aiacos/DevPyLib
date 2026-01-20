"""Luna Builder launcher for mayaLib.

Provides a launcher function for the Luna visual rig builder.
"""


def launch_builder():
    """Launch the Luna visual rig builder.

    Opens the Luna Builder window - a node-based visual editor
    for creating and managing character rigs. The builder provides:
    - Drag-and-drop component creation
    - Visual connection of rig components
    - Graph save/load functionality
    - Real-time rig preview

    Returns:
        BuilderMainWindow: The Luna Builder window instance.

    Example:
        >>> launch_builder()

    """
    from luna_builder import BuilderMainWindow

    BuilderMainWindow.display()
    return BuilderMainWindow.INSTANCE
