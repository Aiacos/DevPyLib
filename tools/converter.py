#!/usr/bin/env python
"""
Cross-platform converter script for DevPyLib texture tools.

This script automatically detects its location and runs texture_tools.py
without requiring hardcoded paths.

Usage:
    python converter.py [args]
"""

import sys
import subprocess
from pathlib import Path


def main():
    # Auto-detect the tools directory based on this script's location
    script_dir = Path(__file__).parent.resolve()
    texture_tools_path = script_dir / "texture_tools.py"

    if not texture_tools_path.exists():
        print(f"Error: texture_tools.py not found at {texture_tools_path}")
        sys.exit(1)

    # Run texture_tools.py with any arguments passed to this script
    try:
        result = subprocess.run(
            [sys.executable, str(texture_tools_path)] + sys.argv[1:],
            check=True
        )
        sys.exit(result.returncode)
    except subprocess.CalledProcessError as e:
        print(f"Error running texture_tools.py: {e}")
        sys.exit(e.returncode)
    except Exception as e:
        print(f"Unexpected error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
