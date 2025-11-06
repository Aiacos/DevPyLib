#!/bin/bash
# ============================================================================
# Maya Test Runner
#
# Runs pytest with mayapy (Maya's Python interpreter) instead of system Python.
# This ensures all Maya and PyMEL imports work correctly during testing.
#
# Usage:
#   ./scripts/test_with_maya.sh                    # Run all tests
#   ./scripts/test_with_maya.sh -v                 # Verbose output
#   ./scripts/test_with_maya.sh -k test_control    # Run specific test
#   ./scripts/test_with_maya.sh -m unit            # Run only unit tests
#   ./scripts/test_with_maya.sh --cov=mayaLib      # With coverage
#
# Environment Variables:
#   MAYA_VERSION: Maya version to use (default: 2024)
#   MAYAPY_PATH: Override mayapy path (auto-detected if not set)
# ============================================================================

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuration
MAYA_VERSION=${MAYA_VERSION:-2024}
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

# Function to print colored messages
info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Function to detect mayapy
detect_mayapy() {
    # Try using detect_mayapy.py script
    if [ -f "$SCRIPT_DIR/detect_mayapy.py" ]; then
        local detected=$(python3 "$SCRIPT_DIR/detect_mayapy.py" 2>/dev/null || true)
        if [ -n "$detected" ] && [ -f "$detected" ]; then
            echo "$detected"
            return 0
        fi
    fi

    # Fallback to common paths based on OS
    local os_type=$(uname -s)
    case "$os_type" in
        Linux)
            local candidates=(
                "/usr/autodesk/maya${MAYA_VERSION}/bin/mayapy"
                "/usr/autodesk/maya2024/bin/mayapy"
                "/usr/autodesk/maya2023/bin/mayapy"
                "/opt/autodesk/maya${MAYA_VERSION}/bin/mayapy"
            )
            ;;
        Darwin)
            local candidates=(
                "/Applications/Autodesk/maya${MAYA_VERSION}/Maya.app/Contents/bin/mayapy"
                "/Applications/Autodesk/maya2024/Maya.app/Contents/bin/mayapy"
                "/Applications/Autodesk/maya2023/Maya.app/Contents/bin/mayapy"
            )
            ;;
        *)
            error "Unsupported OS: $os_type"
            return 1
            ;;
    esac

    for mayapy in "${candidates[@]}"; do
        if [ -f "$mayapy" ]; then
            echo "$mayapy"
            return 0
        fi
    done

    return 1
}

# Main script
main() {
    info "DevPyLib Test Runner with mayapy"
    echo ""

    # Detect or use provided mayapy path
    if [ -n "$MAYAPY_PATH" ]; then
        MAYAPY="$MAYAPY_PATH"
        info "Using provided MAYAPY_PATH: $MAYAPY"
    else
        info "Detecting mayapy installation..."
        MAYAPY=$(detect_mayapy)
        if [ -z "$MAYAPY" ]; then
            error "mayapy not found!"
            echo ""
            echo "Please install Autodesk Maya or set MAYAPY_PATH environment variable:"
            echo "  export MAYAPY_PATH=/path/to/mayapy"
            echo "  $0 $@"
            exit 1
        fi
        info "Found mayapy: $MAYAPY"
    fi

    # Verify mayapy is executable
    if [ ! -x "$MAYAPY" ]; then
        error "mayapy is not executable: $MAYAPY"
        exit 1
    fi

    # Check mayapy version
    MAYAPY_VERSION=$("$MAYAPY" --version 2>&1 || true)
    info "Python version: $MAYAPY_VERSION"
    echo ""

    # Check if pytest is installed in mayapy
    if ! "$MAYAPY" -m pytest --version > /dev/null 2>&1; then
        warn "pytest not found in mayapy environment"
        echo ""
        echo "Installing pytest in mayapy..."
        "$MAYAPY" -m pip install pytest pytest-cov
        echo ""
    fi

    # Change to project root
    cd "$PROJECT_ROOT"

    # Run tests with mayapy
    info "Running tests with mayapy..."
    echo "Command: $MAYAPY -m pytest $@"
    echo ""

    "$MAYAPY" -m pytest "$@"
    EXIT_CODE=$?

    echo ""
    if [ $EXIT_CODE -eq 0 ]; then
        info "Tests passed! ✅"
    else
        error "Tests failed! ❌"
    fi

    exit $EXIT_CODE
}

# Show help
if [ "$1" = "-h" ] || [ "$1" = "--help" ]; then
    cat << EOF
DevPyLib Test Runner with mayapy

Usage:
    $0 [pytest-options]

Examples:
    $0                              # Run all tests
    $0 -v                           # Verbose output
    $0 -k test_control              # Run specific test
    $0 -m unit                      # Run only unit tests
    $0 --cov=mayaLib                # With coverage
    $0 mayaLib/test/test_control.py # Run specific file

Environment Variables:
    MAYA_VERSION    Maya version to use (default: 2024)
    MAYAPY_PATH     Override mayapy path (auto-detected if not set)

Test Markers:
    -m unit         Unit tests (fast, no Maya scene)
    -m integration  Integration tests (requires Maya scene)
    -m gui          GUI tests (interactive, slow)
    -m slow         Slow tests (> 1 second)

For more pytest options, see: pytest --help
EOF
    exit 0
fi

# Run main function
main "$@"
