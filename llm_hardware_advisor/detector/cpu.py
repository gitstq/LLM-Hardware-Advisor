"""
CPU detection module.

Detects CPU model, core count, architecture, and frequency using
platform and psutil. Falls back gracefully when information is unavailable.
"""

import platform
import subprocess
import sys
from typing import Dict, Optional


def detect_cpu() -> Dict[str, Optional[str]]:
    """
    Detect CPU information.

    Returns:
        A dictionary containing:
        - model: CPU model name (str or None)
        - architecture: CPU architecture (str or None)
        - physical_cores: Number of physical cores (str or None)
        - logical_cores: Number of logical cores (str or None)
        - frequency_mhz: CPU frequency in MHz (str or None)
        - vendor: CPU vendor (str or None)
    """
    info: Dict[str, Optional[str]] = {
        "model": None,
        "architecture": None,
        "physical_cores": None,
        "logical_cores": None,
        "frequency_mhz": None,
        "vendor": None,
    }

    # Detect architecture
    machine = platform.machine().lower()
    arch_map = {
        "x86_64": "x86_64 (64-bit)",
        "amd64": "x86_64 (64-bit)",
        "x86": "x86 (32-bit)",
        "i386": "x86 (32-bit)",
        "i686": "x86 (32-bit)",
        "arm64": "ARM64 (64-bit)",
        "aarch64": "ARM64 (64-bit)",
        "armv7l": "ARMv7 (32-bit)",
        "armv8l": "ARM64 (64-bit)",
    }
    info["architecture"] = arch_map.get(machine, machine)

    # Detect logical core count
    try:
        import psutil
        info["logical_cores"] = str(psutil.cpu_count(logical=True))
        info["physical_cores"] = str(psutil.cpu_count(logical=False))
    except (ImportError, Exception):
        try:
            info["logical_cores"] = str(os.cpu_count())
        except Exception:
            pass

    # Detect frequency
    try:
        import psutil
        freq = psutil.cpu_freq()
        if freq:
            info["frequency_mhz"] = f"{freq.max:.0f}" if freq.max else None
    except (ImportError, Exception):
        pass

    # Detect CPU model and vendor based on platform
    system = platform.system()

    if system == "Darwin":
        _detect_darwin_cpu(info)
    elif system == "Linux":
        _detect_linux_cpu(info)
    elif system == "Windows":
        _detect_windows_cpu(info)

    return info


def _detect_darwin_cpu(info: Dict[str, Optional[str]]) -> None:
    """Detect CPU info on macOS using system_profiler."""
    try:
        result = subprocess.run(
            ["sysctl", "-n", "machdep.cpu.brand_string"],
            capture_output=True,
            text=True,
            timeout=5,
        )
        if result.returncode == 0 and result.stdout.strip():
            info["model"] = result.stdout.strip()
    except (subprocess.TimeoutExpired, FileNotFoundError, OSError):
        pass

    # Try system_profiler as fallback
    if not info["model"]:
        try:
            result = subprocess.run(
                ["system_profiler", "SPHardwareDataType"],
                capture_output=True,
                text=True,
                timeout=10,
            )
            if result.returncode == 0:
                for line in result.stdout.splitlines():
                    if "Chip" in line or "Processor" in line:
                        parts = line.split(":", 1)
                        if len(parts) == 2:
                            info["model"] = parts[1].strip()
                            break
        except (subprocess.TimeoutExpired, FileNotFoundError, OSError):
            pass

    # Detect vendor
    if info["model"]:
        model_lower = info["model"].lower()
        if "apple" in model_lower:
            info["vendor"] = "Apple"
        elif "intel" in model_lower:
            info["vendor"] = "Intel"


def _detect_linux_cpu(info: Dict[str, Optional[str]]) -> None:
    """Detect CPU info on Linux by reading /proc/cpuinfo."""
    try:
        with open("/proc/cpuinfo", "r", encoding="utf-8", errors="ignore") as f:
            for line in f:
                line = line.strip()
                if line.startswith("model name"):
                    parts = line.split(":", 1)
                    if len(parts) == 2 and not info["model"]:
                        info["model"] = parts[1].strip()
                elif line.startswith("vendor_id"):
                    parts = line.split(":", 1)
                    if len(parts) == 2 and not info["vendor"]:
                        vendor = parts[1].strip()
                        vendor_map = {
                            "GenuineIntel": "Intel",
                            "AuthenticAMD": "AMD",
                            "ARM": "ARM",
                        }
                        info["vendor"] = vendor_map.get(vendor, vendor)
    except (OSError, IOError):
        pass

    # Fallback: try lscpu
    if not info["model"]:
        try:
            result = subprocess.run(
                ["lscpu"],
                capture_output=True,
                text=True,
                timeout=5,
            )
            if result.returncode == 0:
                for line in result.stdout.splitlines():
                    if "Model name" in line:
                        parts = line.split(":", 1)
                        if len(parts) == 2:
                            info["model"] = parts[1].strip()
                            break
        except (subprocess.TimeoutExpired, FileNotFoundError, OSError):
            pass


def _detect_windows_cpu(info: Dict[str, Optional[str]]) -> None:
    """Detect CPU info on Windows using wmic or registry."""
    try:
        result = subprocess.run(
            ["wmic", "cpu", "get", "Name", "/format:value"],
            capture_output=True,
            text=True,
            timeout=10,
        )
        if result.returncode == 0:
            for line in result.stdout.splitlines():
                line = line.strip()
                if line.startswith("Name="):
                    info["model"] = line[5:].strip()
                    break
    except (subprocess.TimeoutExpired, FileNotFoundError, OSError):
        pass

    # Detect vendor on Windows
    if info["model"]:
        model_lower = info["model"].lower()
        if "intel" in model_lower:
            info["vendor"] = "Intel"
        elif "amd" in model_lower:
            info["vendor"] = "AMD"
