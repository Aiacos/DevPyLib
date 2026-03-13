#!/usr/bin/env bash
# ============================================================================
# DevPyLib Installer for Autodesk Maya (Linux / macOS)
#
# Copies Maya.env and userSetup.py to the correct Maya directories.
# Run from the DevPyLib root directory.
#
# Usage:
#   ./install.sh              Copy files (default)
#   ./install.sh --symlink    Create symlink for userSetup.py instead of copy
# ============================================================================

set -euo pipefail

DEVPYLIB_DIR="$(cd "$(dirname "$0")" && pwd)"
MAYA_ENV_SRC="$DEVPYLIB_DIR/mayaLib/Maya.env"
USERSETUP_SRC="$DEVPYLIB_DIR/mayaLib/userSetup.py"

# --- Parse arguments ---
USE_SYMLINK=0
if [[ "${1:-}" == "--symlink" || "${1:-}" == "-s" ]]; then
    USE_SYMLINK=1
fi

# Detect OS and set Maya base directory
case "$(uname -s)" in
    Darwin)
        MAYA_BASE="$HOME/Library/Preferences/Autodesk/maya"
        MAYA_SCRIPTS_DIR="$MAYA_BASE/scripts"
        ;;
    Linux)
        if [ -d "$HOME/maya" ]; then
            MAYA_BASE="$HOME/maya"
        elif [ -d "$HOME/Documents/maya" ]; then
            MAYA_BASE="$HOME/Documents/maya"
        else
            MAYA_BASE="$HOME/maya"
        fi
        MAYA_SCRIPTS_DIR="$MAYA_BASE/scripts"
        ;;
    MINGW*|MSYS*|CYGWIN*)
        MAYA_BASE="$USERPROFILE/Documents/maya"
        # Convert backslashes if needed
        MAYA_BASE="${MAYA_BASE//\\//}"
        MAYA_SCRIPTS_DIR="$MAYA_BASE/scripts"
        ;;
    *)
        echo "[!!] Unsupported OS: $(uname -s)"
        exit 1
        ;;
esac

echo ""
echo "=== DevPyLib Installer ==="
echo ""
echo "Source directory: $DEVPYLIB_DIR"
echo "Maya base:       $MAYA_BASE"
if [ "$USE_SYMLINK" -eq 1 ]; then
    echo "Mode:            symlink"
else
    echo "Mode:            copy"
fi
echo ""

# --- Detect installed Maya versions ---
FOUND_MAYA=0
for VERSION in 2022 2023 2024 2025 2026; do
    MAYA_VER_DIR="$MAYA_BASE/$VERSION"
    if [ -d "$MAYA_VER_DIR" ]; then
        echo "[OK] Maya $VERSION detected"
        FOUND_MAYA=1

        # Maya.env is always copied (each version needs different content)
        cp "$MAYA_ENV_SRC" "$MAYA_VER_DIR/Maya.env"

        # Replace Maya2024 references with the correct version (compatible with macOS and Linux)
        if [[ "$(uname -s)" == "Darwin" ]]; then
            sed -i '' "s/Maya2024/Maya${VERSION}/g" "$MAYA_VER_DIR/Maya.env"
        else
            sed -i "s/Maya2024/Maya${VERSION}/g" "$MAYA_VER_DIR/Maya.env"
        fi

        echo "     Copied Maya.env to maya/$VERSION/Maya.env (refs updated to Maya${VERSION})"
    fi
done

if [ "$FOUND_MAYA" -eq 0 ]; then
    echo "[!!] No Maya version directories found in $MAYA_BASE"
    echo "     Please install Maya first, or create the directory manually."
    exit 1
fi

# --- Install userSetup.py to shared scripts directory ---
echo ""
mkdir -p "$MAYA_SCRIPTS_DIR"

DEST="$MAYA_SCRIPTS_DIR/userSetup.py"

if [ -f "$DEST" ] || [ -L "$DEST" ]; then
    echo "[!!] userSetup.py already exists at $MAYA_SCRIPTS_DIR"
    read -rp "     Overwrite? (y/N): " OVERWRITE
    if [[ ! "$OVERWRITE" =~ ^[Yy]$ ]]; then
        echo "     Skipped userSetup.py"
        echo ""
        echo "=== Installation Complete ==="
        exit 0
    fi
    rm -f "$DEST"
fi

if [ "$USE_SYMLINK" -eq 1 ]; then
    ln -s "$USERSETUP_SRC" "$DEST"
    echo "[OK] Symlinked userSetup.py -> $USERSETUP_SRC"
else
    cp "$USERSETUP_SRC" "$DEST"
    echo "[OK] Copied userSetup.py to $MAYA_SCRIPTS_DIR"
fi

echo ""
echo "=== Installation Complete ==="
echo ""
echo "Files installed:"
echo "  Maya.env     -> maya/{version}/Maya.env  (per-version, always copied)"
if [ "$USE_SYMLINK" -eq 1 ]; then
    echo "  userSetup.py -> maya/scripts/userSetup.py (symlink)"
else
    echo "  userSetup.py -> maya/scripts/userSetup.py (copy)"
fi
echo ""
echo "To disable Luna at startup, ensure Maya.env contains:"
echo "  DEVPYLIB_DISABLE_LUNA=1"
echo ""
