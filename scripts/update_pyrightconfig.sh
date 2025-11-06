#!/bin/bash
# ============================================================================
# Update pyrightconfig.json with detected mayapy paths
#
# This script auto-detects mayapy and updates pyrightconfig.json with the
# correct paths. Useful when:
# - Switching Maya versions
# - Moving to a different machine
# - After Maya installation/upgrade
#
# Usage:
#   ./scripts/update_pyrightconfig.sh           # Auto-detect and update
#   ./scripts/update_pyrightconfig.sh --dry-run # Show changes without applying
#   ./scripts/update_pyrightconfig.sh --help    # Show help
# ============================================================================

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
PYRIGHT_CONFIG="$PROJECT_ROOT/pyrightconfig.json"

# Help text
show_help() {
    cat << EOF
Update pyrightconfig.json with detected mayapy paths

Usage:
    $0 [OPTIONS]

Options:
    --dry-run       Show what would be changed without applying
    --maya-version  Specify Maya version (e.g., 2024, 2023)
    --help          Show this help message

Examples:
    $0                              # Auto-detect and update
    $0 --dry-run                    # Preview changes
    $0 --maya-version 2023          # Use specific Maya version

This script:
  1. Detects mayapy installation
  2. Gets Python version and site-packages path
  3. Updates pyrightconfig.json with correct paths
  4. Validates JSON syntax
EOF
}

# Parse arguments
DRY_RUN=false
MAYA_VERSION=""

while [[ $# -gt 0 ]]; do
    case $1 in
        --dry-run)
            DRY_RUN=true
            shift
            ;;
        --maya-version)
            MAYA_VERSION="$2"
            shift 2
            ;;
        --help|-h)
            show_help
            exit 0
            ;;
        *)
            echo "Unknown option: $1"
            show_help
            exit 1
            ;;
    esac
done

echo -e "${BLUE}DevPyLib pyrightconfig.json Updater${NC}"
echo ""

# Check if pyrightconfig.json exists
if [ ! -f "$PYRIGHT_CONFIG" ]; then
    echo -e "${RED}Error: pyrightconfig.json not found at: $PYRIGHT_CONFIG${NC}"
    exit 1
fi

# Detect mayapy
echo -e "${YELLOW}→${NC} Detecting mayapy installation..."

if [ -f "$SCRIPT_DIR/detect_mayapy.py" ]; then
    MAYAPY_INFO=$(python3 "$SCRIPT_DIR/detect_mayapy.py" --json 2>/dev/null || echo "")
else
    echo -e "${RED}Error: detect_mayapy.py not found${NC}"
    exit 1
fi

if [ -z "$MAYAPY_INFO" ]; then
    echo -e "${RED}Error: No Maya installation found${NC}"
    echo "Please install Autodesk Maya or specify MAYAPY_PATH manually"
    exit 1
fi

# Parse JSON (requires jq or python)
if command -v jq &> /dev/null; then
    MAYAPY_PATH=$(echo "$MAYAPY_INFO" | jq -r '.mayapy')
    MAYA_VERSION_DETECTED=$(echo "$MAYAPY_INFO" | jq -r '.version')
    PYTHON_VERSION=$(echo "$MAYAPY_INFO" | jq -r '.python')
    SITE_PACKAGES=$(echo "$MAYAPY_INFO" | jq -r '.site_packages')
else
    # Fallback to python for JSON parsing
    MAYAPY_PATH=$(echo "$MAYAPY_INFO" | python3 -c "import sys, json; print(json.load(sys.stdin)['mayapy'])")
    MAYA_VERSION_DETECTED=$(echo "$MAYAPY_INFO" | python3 -c "import sys, json; print(json.load(sys.stdin)['version'])")
    PYTHON_VERSION=$(echo "$MAYAPY_INFO" | python3 -c "import sys, json; print(json.load(sys.stdin)['python'])")
    SITE_PACKAGES=$(echo "$MAYAPY_INFO" | python3 -c "import sys, json; print(json.load(sys.stdin)['site_packages'])")
fi

echo -e "${GREEN}✓${NC} Found Maya installation:"
echo "  Version:       $MAYA_VERSION_DETECTED"
echo "  mayapy:        $MAYAPY_PATH"
echo "  Python:        $PYTHON_VERSION"
echo "  site-packages: $SITE_PACKAGES"
echo ""

# Extract Python version number (e.g., "3.10" from "Python 3.10.8")
PYTHON_VER=$(echo "$PYTHON_VERSION" | grep -oP '\d+\.\d+' | head -1)

if [ -z "$PYTHON_VER" ]; then
    echo -e "${YELLOW}Warning: Could not detect Python version, using 3.10${NC}"
    PYTHON_VER="3.10"
fi

# Prepare updated config
echo -e "${YELLOW}→${NC} Preparing pyrightconfig.json update..."

# Create backup
BACKUP_FILE="$PYRIGHT_CONFIG.backup.$(date +%Y%m%d_%H%M%S)"
cp "$PYRIGHT_CONFIG" "$BACKUP_FILE"
echo -e "${GREEN}✓${NC} Backup created: $BACKUP_FILE"

# Update pyrightconfig.json using Python
UPDATE_SCRIPT=$(cat <<EOF
import json
import sys

config_file = '$PYRIGHT_CONFIG'
python_version = '$PYTHON_VER'
site_packages = '$SITE_PACKAGES'

# Read config
with open(config_file, 'r') as f:
    config = json.load(f)

# Update python version
config['pythonVersion'] = python_version

# Update execution environments
if 'executionEnvironments' in config:
    for env in config['executionEnvironments']:
        if 'extraPaths' in env:
            # Replace or add site-packages
            env['extraPaths'] = [site_packages]
        else:
            env['extraPaths'] = [site_packages]

# Print updated config (for dry-run)
print(json.dumps(config, indent=2))

# Write if not dry-run
if len(sys.argv) > 1 and sys.argv[1] == 'write':
    with open(config_file, 'w') as f:
        json.dump(config, f, indent=2)
    print('\nConfig written to: ' + config_file, file=sys.stderr)
EOF
)

if [ "$DRY_RUN" = true ]; then
    echo ""
    echo -e "${BLUE}=== Dry Run (no changes will be made) ===${NC}"
    echo ""
    python3 -c "$UPDATE_SCRIPT"
    echo ""
    echo -e "${YELLOW}→${NC} No changes applied (dry-run mode)"
    echo "  Run without --dry-run to apply changes"
else
    python3 -c "$UPDATE_SCRIPT" write > /dev/null
    echo -e "${GREEN}✓${NC} pyrightconfig.json updated successfully"

    # Validate JSON
    if python3 -c "import json; json.load(open('$PYRIGHT_CONFIG'))" 2>/dev/null; then
        echo -e "${GREEN}✓${NC} JSON syntax is valid"
    else
        echo -e "${RED}✗${NC} JSON syntax error! Restoring backup..."
        cp "$BACKUP_FILE" "$PYRIGHT_CONFIG"
        exit 1
    fi

    echo ""
    echo -e "${GREEN}Done!${NC} pyrightconfig.json has been updated with:"
    echo "  Python version: $PYTHON_VER"
    echo "  extraPaths: $SITE_PACKAGES"
    echo ""
    echo "Restart your LSP in Neovim:"
    echo "  :LspRestart"
fi

# Clean up old backups (keep last 5)
BACKUP_COUNT=$(ls -1 "$PROJECT_ROOT"/pyrightconfig.json.backup.* 2>/dev/null | wc -l)
if [ "$BACKUP_COUNT" -gt 5 ]; then
    echo ""
    echo -e "${YELLOW}→${NC} Cleaning old backups (keeping last 5)..."
    ls -1t "$PROJECT_ROOT"/pyrightconfig.json.backup.* | tail -n +6 | xargs rm -f
    echo -e "${GREEN}✓${NC} Cleanup complete"
fi
