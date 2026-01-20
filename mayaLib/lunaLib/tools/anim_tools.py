"""Luna animation tool launchers for mayaLib.

Provides launcher functions for Luna's animation tools.
"""


def launch_anim_baker():
    """Launch the Luna animation baker tool.

    Opens the animation baker window for baking animation data
    between different control systems or spaces.

    Returns:
        None: Opens the anim baker window.

    Example:
        >>> launch_anim_baker()

    """
    from luna.tools import anim_baker

    anim_baker.AnimBakerDialog.display()


def launch_keyframe_transfer():
    """Launch the Luna keyframe transfer tool.

    Opens the keyframe transfer window for copying animation
    between controls or characters.

    Returns:
        None: Opens the keyframe transfer window.

    Example:
        >>> launch_keyframe_transfer()

    """
    from luna.tools import transfer_keyframes

    transfer_keyframes.TransferKeyframesDialog.display()


def launch_space_tool():
    """Launch the Luna custom space tool.

    Opens the custom space tool for creating and managing
    custom parent spaces for controls.

    Returns:
        None: Opens the space tool window.

    Example:
        >>> launch_space_tool()

    """
    from luna.tools import custom_space_tool

    custom_space_tool.CustomSpaceDialog.display()
