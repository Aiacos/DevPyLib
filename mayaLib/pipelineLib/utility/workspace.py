import maya.cmds as cmd
import pymel.core as pm


def get_current_workspace(debug=True):
    """Get the current Maya workspace.

    Args:
        debug (bool): If True, print the current workspace to the console.

    Returns:
        str: The current Maya workspace.
    """
    workspace = pm.workspace(rd=True, q=True)
    if debug:
        print(workspace)
    return workspace


def set_workspace_to_filepath(file_path=None, debug=True):
    """Set the current Maya workspace to the given file path.

    If no file path is provided, the current scene's directory is used.

    Args:
        file_path (str): The file path to set as the current workspace.
        debug (bool): If True, print the current workspace to the console.
    """
    if file_path is None:
        file_path = '/'.join(cmd.file(q=True, sn=True).split('/')[:-1]) + '/'
    pm.workspace(file_path, openWorkspace=True)
    if debug:
        get_current_workspace(debug)


if __name__ == '__main__':
    set_workspace_to_filepath()