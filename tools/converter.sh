#!/bin/bash
#
# Cross-platform shell script for DevPyLib texture tools (Linux/macOS)
#
# This script automatically detects its location and runs texture_tools.py
# without requiring hardcoded paths.
#
# Usage:
#   ./converter.sh [args]
#   bash converter.sh [args]
#

# Get the directory where this script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
TEXTURE_TOOLS="${SCRIPT_DIR}/texture_tools.py"

# Check if texture_tools.py exists
if [ ! -f "$TEXTURE_TOOLS" ]; then
    echo "Error: texture_tools.py not found at ${TEXTURE_TOOLS}"
    exit 1
fi

# Run texture_tools.py with any arguments passed to this script
python3 "$TEXTURE_TOOLS" "$@"
