"""
Memory detection module.

Detects total and available system RAM using psutil.
"""

from typing import Dict, Optional

try:
    import psutil
    HAS_PSUTIL = True
except ImportError:
    HAS_PSUTIL = False


def detect_memory() -> Dict[str, Optional[str]]:
    """
    Detect system memory information.

    Returns:
        A dictionary containing:
        - total_gb: Total RAM in GB (str or None)
        - available_gb: Available RAM in GB (str or None)
        - used_gb: Used RAM in GB (str or None)
        - percent_used: Percentage of RAM used (str or None)
    """
    info: Dict[str, Optional[str]] = {
        "total_gb": None,
        "available_gb": None,
        "used_gb": None,
        "percent_used": None,
    }

    if not HAS_PSUTIL:
        return info

    try:
        mem = psutil.virtual_memory()
        info["total_gb"] = f"{mem.total / (1024 ** 3):.1f}"
        info["available_gb"] = f"{mem.available / (1024 ** 3):.1f}"
        info["used_gb"] = f"{mem.used / (1024 ** 3):.1f}"
        info["percent_used"] = f"{mem.percent:.1f}"
    except Exception:
        pass

    return info
