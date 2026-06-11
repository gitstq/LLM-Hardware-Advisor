#!/usr/bin/env python3
"""
PyInstaller build script for LLM Hardware Advisor.

Creates a single-file executable for distribution.
Requires: pip install pyinstaller
"""

import os
import subprocess
import sys
from typing import List


def main() -> None:
    """Build a single-file executable using PyInstaller."""
    project_root = os.path.dirname(os.path.abspath(__file__))

    # Check if PyInstaller is installed
    try:
        import PyInstaller  # noqa: F401
    except ImportError:
        print("PyInstaller is not installed. Installing...")
        subprocess.check_call(
            [sys.executable, "-m", "pip", "install", "pyinstaller>=5.0"],
            cwd=project_root,
        )

    # Build command
    cmd: List[str] = [
        sys.executable,
        "-m",
        "PyInstaller",
        "--onefile",                    # Single file executable
        "--name=llm-advisor",           # Output name
        "--clean",                      # Clean build cache
        "--noconfirm",                  # Overwrite without asking
        f"--add-data={os.path.join(project_root, 'llm_hardware_advisor', 'database', 'models.json')}:llm_hardware_advisor/database",  # noqa: E501
        os.path.join(project_root, "llm_hardware_advisor", "cli.py"),
    ]

    print(f"Building llm-advisor executable...")
    print(f"Command: {' '.join(cmd)}")
    print()

    result = subprocess.run(cmd, cwd=project_root)

    if result.returncode == 0:
        output_path = os.path.join(project_root, "dist", "llm-advisor")
        if sys.platform == "win32":
            output_path += ".exe"
        print()
        print(f"Build successful! Executable: {output_path}")
        print(f"Size: {os.path.getsize(output_path) / (1024 * 1024):.1f} MB")
    else:
        print(f"Build failed with return code {result.returncode}")
        sys.exit(1)


if __name__ == "__main__":
    main()
