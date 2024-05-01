import pymel.core as pm
import maya.cmds as cmd


def get_current_workspace(debug=True):
    workspace = pm.workspace(rd=True, q=True)
    
    if debug:
        print(workspace)
    
    return workspace
    
def set_workspace_to_filepath(file_path = str('/'.join(cmd.file(q=True, sn=True).split('/')[:-1]) + '/'), debug=True):
    pm.workspace(file_path, openWorkspace=True)
    
    if debug:
        get_current_workspace(debug)


if __name__ == "__main__":
    set_workspace_to_filepath()