"""
System information detection module.

Detects OS type/version, disk space, Python version, and other system-level info.
"""

import os
import platform
import shutil
import subprocess
import sys
from typing import Dict, Optional


def detect_system() -> Dict[str, Optional[str]]:
    """
    Detect system-level information.

    Returns:
        A dictionary containing:
        - os_name: Operating system name (str or None)
        - os_version: OS version (str or None)
        - os_release: OS release string (str or None)
        - python_version: Python version (str or None)
        - disk_total_gb: Total disk space in GB (str or None)
        - disk_free_gb: Free disk space in GB (str or None)
        - hostname: Machine hostname (str or None)
        - architecture: System architecture (str or None)
    """
    info: Dict[str, Optional[str]] = {
        "os_name": None,
        "os_version": None,
        "os_release": None,
        "python_version": None,
        "disk_total_gb": None,
        "disk_free_gb": None,
        "hostname": None,
        "architecture": None,
    }

    # OS information
    info["os_name"] = platform.system()
    info["os_version"] = platform.version()
    info["os_release"] = platform.release()

    # Python version
    info["python_version"] = f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"

    # Hostname
    try:
        info["hostname"] = platform.node()
    except Exception:
        pass

    # Architecture
    info["architecture"] = platform.machine()

    # Disk space (current working directory)
    try:
        disk_usage = shutil.disk_usage(os.getcwd())
        info["disk_total_gb"] = f"{disk_usage.total / (1024 ** 3):.1f}"
        info["disk_free_gb"] = f"{disk_usage.free / (1024 ** 3):.1f}"
    except Exception:
        pass

    # Enhanced OS info for Linux distributions
    if info["os_name"] == "Linux":
        _detect_linux_distro(info)

    return info


def _detect_linux_distro(info: Dict[str, Optional[str]]) -> None:
    """Detect Linux distribution name and version."""
    # Try /etc/os-release first (most reliable)
    os_release_path = "/etc/os-release"
    try:
        with open(os_release_path, "r", encoding="utf-8", errors="ignore") as f:
            for line in f:
                line = line.strip()
                if line.startswith("PRETTY_NAME="):
                    value = line.split("=", 1)[1].strip().strip('"')
                    info["os_name"] = value
                    break
                elif line.startswith("VERSION_ID=") and not info["os_version"]:
                    value = line.split("=", 1)[1].strip().strip('"')
                    info["os_version"] = value
    except (OSError, IOError):
        pass

    # Fallback: try lsb_release
    if info["os_name"] == "Linux":
        try:
            result = subprocess.run(
                ["lsb_release", "-d"],
                capture_output=True,
                text=True,
                timeout=5,
            )
            if result.returncode == 0:
                parts = result.stdout.strip().split(":", 1)
                if len(parts) == 2:
                    info["os_name"] = parts[1].strip()
        except (subprocess.TimeoutExpired, FileNotFoundError, OSError):
            pass
