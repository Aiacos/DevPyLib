import importlib
import os
import sys
from pathlib import Path
from git import Repo, GitCommandError

import maya.cmds as cmds


def git_pull_gitpython(repo_path: str | Path, branch: str = "master") -> None:
    """
    Pulls the specified branch from a remote Git repository, using the GitPython library.

    Args:
        repo_path (str | Path): The path to the local Git repository.
        branch (str, optional): The branch to pull from the remote. Defaults to "main".

    Notes:
        This function is equivalent to running `git pull --ff-only origin <branch>`.
        If a Git error occurs, the error message is printed and the function exits.
    """
    repo = Repo(Path(repo_path).expanduser().resolve())
    try:
        # ensure we’re on the branch we want
        repo.git.checkout(branch)

        # equivalent to `git pull --ff-only`
        pull_info = repo.remotes.origin.pull(branch, ff_only=True)
        for info in pull_info:  # print or log each updated ref
            print(f"{info.ref} – {info.summary}")
    except GitCommandError as exc:
        print(f"Git error: {exc}")
        # handle merge conflicts, auth errors, etc. here


def install_requirements(requiremensts_dir):
    """
    Installs the Python packages listed in the requirements.txt file located in the specified directory.

    Args:
        requiremensts_dir (str): The directory path where the requirements.txt file is located.

    Raises:
        Exception: If an error occurs during the installation process, an exception is caught and its message is printed.
    """
    try:
        os.system("pip install -r " + requiremensts_dir + "/requirements.txt")
        print("All requirements installed successfully!")
    except Exception as e:
        print(f"An error occurred: {e}")


libDir = (Path.home() / "Documents" / "workspace" / "DevPyLib").as_posix()
port = "4434"
libName = "mayaLib"

install_requirements(libDir)
# git_pull_gitpython(libDir, branch="develop")

# Open Maya port
try:
    if not cmds.commandPort(port, q=True):
        cmds.commandPort(n=port)
except:
    pass

# Add develpment PATH
if not libDir in sys.path:
    sys.path.append(libDir)
    __import__(libName)
else:
    importlib.reload(__import__(libName))
    # reload(__import__(libName))


command = str(
    "import mayaLib.guiLib.mainMenu as mm; libmenu = mm.MainMenu('" + str(libDir) + "')"
)
cmds.evalDeferred(command, lowestPriority=True)
