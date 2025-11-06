#!/usr/bin/env python3
"""Auto-detect mayapy path for LSP and testing configuration.

This script searches for Maya's Python interpreter (mayapy) on the system
and returns the path for use in Neovim LSP, pytest, and other tools.

Usage:
    python3 scripts/detect_mayapy.py                    # Print mayapy path
    python3 scripts/detect_mayapy.py --version          # Print Maya version
    python3 scripts/detect_mayapy.py --site-packages   # Print site-packages path
    python3 scripts/detect_mayapy.py --all-versions    # List all Maya installations
"""

from __future__ import annotations

import os
import platform
import subprocess
import sys
from pathlib import Path
from typing import NamedTuple


class MayaInstallation(NamedTuple):
    """Information about a Maya installation."""

    version: str
    mayapy_path: Path
    python_version: str
    site_packages: Path


def find_maya_installations_linux() -> list[MayaInstallation]:
    """Find Maya installations on Linux."""
    installations = []
    base_path = Path('/usr/autodesk')

    if not base_path.exists():
        return installations

    for maya_dir in sorted(base_path.glob('maya*'), reverse=True):
        mayapy = maya_dir / 'bin' / 'mayapy'
        if mayapy.exists() and os.access(mayapy, os.X_OK):
            try:
                # Get Python version from mayapy
                result = subprocess.run(
                    [str(mayapy), '--version'],
                    capture_output=True,
                    text=True,
                    timeout=5,
                    check=False,
                )
                python_version = result.stderr.strip() if result.stderr else 'Unknown'

                # Find site-packages
                site_packages_candidates = [
                    maya_dir / 'lib' / 'python3.10' / 'site-packages',
                    maya_dir / 'lib' / 'python3.9' / 'site-packages',
                    maya_dir / 'lib' / 'python3.11' / 'site-packages',
                ]
                site_packages = next(
                    (p for p in site_packages_candidates if p.exists()),
                    maya_dir / 'lib',
                )

                installations.append(
                    MayaInstallation(
                        version=maya_dir.name,
                        mayapy_path=mayapy,
                        python_version=python_version,
                        site_packages=site_packages,
                    )
                )
            except (subprocess.TimeoutExpired, OSError):
                continue

    return installations


def find_maya_installations_macos() -> list[MayaInstallation]:
    """Find Maya installations on macOS."""
    installations = []
    base_path = Path('/Applications/Autodesk')

    if not base_path.exists():
        return installations

    for maya_dir in sorted(base_path.glob('maya*/Maya.app'), reverse=True):
        mayapy = maya_dir / 'Contents' / 'bin' / 'mayapy'
        if mayapy.exists() and os.access(mayapy, os.X_OK):
            try:
                result = subprocess.run(
                    [str(mayapy), '--version'],
                    capture_output=True,
                    text=True,
                    timeout=5,
                    check=False,
                )
                python_version = result.stderr.strip() if result.stderr else 'Unknown'

                site_packages_candidates = [
                    maya_dir / 'Contents' / 'Frameworks' / 'Python.framework' / 'Versions' / '3.10' / 'lib' / 'python3.10' / 'site-packages',
                    maya_dir / 'Contents' / 'Frameworks' / 'Python.framework' / 'Versions' / '3.9' / 'lib' / 'python3.9' / 'site-packages',
                ]
                site_packages = next(
                    (p for p in site_packages_candidates if p.exists()),
                    maya_dir / 'Contents' / 'Frameworks',
                )

                installations.append(
                    MayaInstallation(
                        version=maya_dir.parent.name,
                        mayapy_path=mayapy,
                        python_version=python_version,
                        site_packages=site_packages,
                    )
                )
            except (subprocess.TimeoutExpired, OSError):
                continue

    return installations


def find_maya_installations_windows() -> list[MayaInstallation]:
    """Find Maya installations on Windows."""
    installations = []
    base_paths = [
        Path('C:/Program Files/Autodesk'),
        Path('C:/Program Files (x86)/Autodesk'),
    ]

    for base_path in base_paths:
        if not base_path.exists():
            continue

        for maya_dir in sorted(base_path.glob('Maya*'), reverse=True):
            mayapy = maya_dir / 'bin' / 'mayapy.exe'
            if mayapy.exists():
                try:
                    result = subprocess.run(
                        [str(mayapy), '--version'],
                        capture_output=True,
                        text=True,
                        timeout=5,
                        check=False,
                    )
                    python_version = result.stderr.strip() if result.stderr else 'Unknown'

                    site_packages_candidates = [
                        maya_dir / 'Python' / 'Lib' / 'site-packages',
                        maya_dir / 'Python310' / 'Lib' / 'site-packages',
                        maya_dir / 'Python39' / 'Lib' / 'site-packages',
                    ]
                    site_packages = next(
                        (p for p in site_packages_candidates if p.exists()),
                        maya_dir / 'Python',
                    )

                    installations.append(
                        MayaInstallation(
                            version=maya_dir.name,
                            mayapy_path=mayapy,
                            python_version=python_version,
                            site_packages=site_packages,
                        )
                    )
                except (subprocess.TimeoutExpired, OSError):
                    continue

    return installations


def find_maya_installations() -> list[MayaInstallation]:
    """Find all Maya installations on the system."""
    system = platform.system()

    if system == 'Linux':
        return find_maya_installations_linux()
    elif system == 'Darwin':  # macOS
        return find_maya_installations_macos()
    elif system == 'Windows':
        return find_maya_installations_windows()
    else:
        return []


def get_latest_maya() -> MayaInstallation | None:
    """Get the latest Maya installation."""
    installations = find_maya_installations()
    return installations[0] if installations else None


def main() -> int:
    """Main entry point."""
    import argparse

    parser = argparse.ArgumentParser(
        description='Detect mayapy installation for LSP and testing'
    )
    parser.add_argument(
        '--version',
        action='store_true',
        help='Print Maya version and Python version',
    )
    parser.add_argument(
        '--site-packages',
        action='store_true',
        help='Print site-packages path',
    )
    parser.add_argument(
        '--all-versions',
        action='store_true',
        help='List all Maya installations',
    )
    parser.add_argument(
        '--json',
        action='store_true',
        help='Output in JSON format',
    )

    args = parser.parse_args()

    installations = find_maya_installations()

    if not installations:
        print('ERROR: No Maya installation found', file=sys.stderr)
        return 1

    latest = installations[0]

    if args.all_versions:
        if args.json:
            import json

            data = [
                {
                    'version': inst.version,
                    'mayapy': str(inst.mayapy_path),
                    'python': inst.python_version,
                    'site_packages': str(inst.site_packages),
                }
                for inst in installations
            ]
            print(json.dumps(data, indent=2))
        else:
            print('Found Maya installations:')
            for inst in installations:
                print(f'\n{inst.version}:')
                print(f'  mayapy: {inst.mayapy_path}')
                print(f'  Python: {inst.python_version}')
                print(f'  site-packages: {inst.site_packages}')
    elif args.version:
        print(f'{latest.version} ({latest.python_version})')
    elif args.site_packages:
        print(latest.site_packages)
    elif args.json:
        import json

        data = {
            'version': latest.version,
            'mayapy': str(latest.mayapy_path),
            'python': latest.python_version,
            'site_packages': str(latest.site_packages),
        }
        print(json.dumps(data, indent=2))
    else:
        # Default: print mayapy path only (for easy use in scripts)
        print(latest.mayapy_path)

    return 0


if __name__ == '__main__':
    sys.exit(main())
