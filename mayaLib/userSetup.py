"""Maya userSetup script for DevPyLib initialization.

Automatically loads DevPyLib library on Maya startup, handles dependency
installation in background thread, opens command port for external connections,
and creates the main menu interface.
"""

import importlib
import os
import subprocess
import sys
import threading
from pathlib import Path

import maya.cmds as cmds
import maya.utils

# Optional git support
try:
    from git import GitCommandError, Repo

    GIT_AVAILABLE = True
except ImportError:
    GIT_AVAILABLE = False
    print("GitPython not available - git operations disabled")


def git_pull_gitpython(repo_path: str | Path, branch: str = "master") -> None:
    """Pull the specified branch from a remote Git repository.

    Args:
        repo_path: The path to the local Git repository.
        branch: The branch to pull from the remote. Defaults to "master".
    """
    if not GIT_AVAILABLE:
        print("GitPython not installed - skipping git pull")
        return

    repo = Repo(Path(repo_path).expanduser().resolve())
    try:
        repo.git.checkout(branch)
        pull_info = repo.remotes.origin.pull(branch, ff_only=True)
        for info in pull_info:
            print(f"{info.ref} - {info.summary}")
    except GitCommandError as exc:
        print(f"Git error: {exc}")


def _check_requirements_satisfied(requirements_file):
    """Check if all requirements are already importable.

    Args:
        requirements_file: Path to requirements.txt.

    Returns:
        True if all packages are importable, False otherwise.
    """
    # Map pip package names to their import names where they differ
    import_name_map = {
        "gitpython": "git",
        "pymel": "pymel",
        "numpy": "numpy",
    }

    with open(requirements_file) as f:
        for line in f:
            pkg = line.strip().lower()
            if not pkg or pkg.startswith("#"):
                continue
            import_name = import_name_map.get(pkg, pkg)
            try:
                importlib.import_module(import_name)
            except ImportError:
                return False
    return True


def _install_requirements_thread(requirements_dir):
    """Background thread function for pip install (no Maya API calls)."""
    requirements_file = Path(requirements_dir) / "requirements.txt"

    if not requirements_file.exists():
        maya.utils.executeDeferred(
            lambda: print(f"Warning: requirements.txt not found at {requirements_file}")
        )
        return

    # Skip pip entirely if all packages are already importable
    if _check_requirements_satisfied(requirements_file):
        maya.utils.executeDeferred(
            lambda: print("All requirements already satisfied — skipping pip install.")
        )
        return

    try:
        result = subprocess.run(
            [sys.executable, "-m", "pip", "install", "-r", str(requirements_file)],
            capture_output=True,
            text=True,
            timeout=300,
        )

        if result.returncode == 0:
            maya.utils.executeDeferred(
                lambda: print("All requirements installed successfully!")
            )
        else:
            maya.utils.executeDeferred(
                lambda: print(f"Error installing requirements: {result.stderr}")
            )

    except subprocess.TimeoutExpired:
        maya.utils.executeDeferred(
            lambda: print("Error: pip install timed out after 5 minutes")
        )
    except (OSError, subprocess.SubprocessError) as e:
        maya.utils.executeDeferred(
            lambda: print(f"An error occurred during installation: {e}")
        )


def install_requirements_async(requirements_dir):
    """Install requirements in a background thread (non-blocking)."""
    thread = threading.Thread(
        target=_install_requirements_thread,
        args=(requirements_dir,),
        daemon=True,
    )
    thread.start()
    print("Installing requirements in background...")


# Get DevPyLib directory from environment variable (set in Maya.env)
lib_dir = os.environ.get("DEVPYLIB_PATH")
port = "4434"
lib_name = "mayaLib"

print(f"DevPyLib detected at: {lib_dir}")

if lib_dir:
    # Install requirements in background thread (non-blocking)
    install_requirements_async(lib_dir)

    # Uncomment to enable auto-pull from git on Maya startup
    # git_pull_gitpython(lib_dir, branch="master")

    # Open Maya command port for external connections
    try:
        if not cmds.commandPort(port, q=True):
            cmds.commandPort(n=port)
            print(f"Maya command port opened on: {port}")
    except RuntimeError as e:
        print(f"Could not open command port {port}: {e}")

    # Add DevPyLib to Python path and import mayaLib
    if lib_dir not in sys.path:
        sys.path.append(lib_dir)
        print(f"Added {lib_dir} to sys.path")

    # Block Luna from auto-loading if DEVPYLIB_DISABLE_LUNA=1
    if os.environ.get("DEVPYLIB_DISABLE_LUNA", "0") == "1":
        # Prevent Python from finding the luna package in DevPyLib
        luna_path = str(Path(lib_dir) / "luna")
        sys.modules["luna"] = None  # Block any future import luna
        sys.modules["luna_builder"] = None
        sys.modules["luna_configer"] = None
        sys.modules["luna_rig"] = None
        print("Luna disabled via DEVPYLIB_DISABLE_LUNA=1")

    try:
        if lib_name in sys.modules:
            importlib.reload(sys.modules[lib_name])
            print(f"Reloaded {lib_name}")
        else:
            __import__(lib_name)
            print(f"Imported {lib_name}")
    except ImportError as e:
        print(f"Error importing {lib_name}: {e}")

    # Create main menu (deferred to ensure Maya UI is ready)
    command = f"import mayaLib.guiLib.main_menu as mm; libmenu = mm.MainMenu('{lib_dir}')"
    cmds.evalDeferred(command, lowestPriority=True)
else:
    print("Warning: DEVPYLIB_PATH not set in Maya.env")

print("DevPyLib setup complete!")
