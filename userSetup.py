import importlib
import sys
import subprocess
from pathlib import Path

import maya.cmds as cmds

# Optional git support
try:
    from git import Repo, GitCommandError

    GIT_AVAILABLE = True
except ImportError:
    GIT_AVAILABLE = False
    print("GitPython not available - git operations disabled")


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
    if not GIT_AVAILABLE:
        print("GitPython not installed - skipping git pull")
        return

    repo = Repo(Path(repo_path).expanduser().resolve())
    try:
        # ensure we're on the branch we want
        repo.git.checkout(branch)

        # equivalent to `git pull --ff-only`
        pull_info = repo.remotes.origin.pull(branch, ff_only=True)
        for info in pull_info:  # print or log each updated ref
            print(f"{info.ref} – {info.summary}")
    except GitCommandError as exc:
        print(f"Git error: {exc}")
        # handle merge conflicts, auth errors, etc. here


def install_requirements(requirements_dir):
    """
    Installs the Python packages listed in the requirements.txt file located in the specified directory.

    Args:
        requirements_dir (str | Path): The directory path where the requirements.txt file is located.

    Returns:
        bool: True if installation was successful, False otherwise.
    """
    requirements_file = Path(requirements_dir) / "requirements.txt"

    if not requirements_file.exists():
        print(f"Warning: requirements.txt not found at {requirements_file}")
        return False

    try:
        # Use subprocess instead of os.system for better cross-platform support
        result = subprocess.run(
            [sys.executable, "-m", "pip", "install", "-r", str(requirements_file)],
            capture_output=True,
            text=True,
            timeout=300,  # 5 minutes timeout
        )

        if result.returncode == 0:
            print("All requirements installed successfully!")
            return True
        else:
            print(f"Error installing requirements: {result.stderr}")
            return False

    except subprocess.TimeoutExpired:
        print("Error: pip install timed out after 5 minutes")
        return False
    except Exception as e:
        print(f"An error occurred during installation: {e}")
        return False


# Auto-detect DevPyLib directory based on this file's location
# This allows the library to work from any location without hardcoded paths
libDir = Path(__file__).parent.resolve().as_posix()
port = "4434"
libName = "mayaLib"

print(f"DevPyLib detected at: {libDir}")

install_requirements(libDir)
# Uncomment to enable auto-pull from git on Maya startup
# git_pull_gitpython(libDir, branch="master")

# Open Maya command port for external connections
try:
    if not cmds.commandPort(port, q=True):
        cmds.commandPort(n=port)
        print(f"Maya command port opened on: {port}")
except Exception as e:
    print(f"Could not open command port {port}: {e}")

# Add DevPyLib to Python path and import mayaLib
if libDir not in sys.path:
    sys.path.append(libDir)
    print(f"Added {libDir} to sys.path")

try:
    if libName in sys.modules:
        # Reload if already imported
        importlib.reload(sys.modules[libName])
        print(f"Reloaded {libName}")
    else:
        # First import
        __import__(libName)
        print(f"Imported {libName}")
except ImportError as e:
    print(f"Error importing {libName}: {e}")

# Create main menu (deferred to ensure Maya UI is ready)
command = f"import mayaLib.guiLib.mainMenu as mm; libmenu = mm.MainMenu('{libDir}')"
cmds.evalDeferred(command, lowestPriority=True)

print("DevPyLib setup complete!")
