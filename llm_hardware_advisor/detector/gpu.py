"""
GPU detection module.

Detects GPU information for NVIDIA, AMD, Apple Silicon, and Intel Arc GPUs.
Uses subprocess calls to system utilities (nvidia-smi, rocm-smi, system_profiler,
lspci, intel_gpu_top) without requiring third-party Python GPU libraries.
"""

import json
import platform
import re
import subprocess
from typing import Dict, List, Optional


def detect_gpus() -> List[Dict[str, Optional[str]]]:
    """
    Detect all available GPUs in the system.

    Tries detection methods in order: NVIDIA -> AMD -> Apple Silicon -> Intel Arc.

    Returns:
        A list of GPU info dictionaries, each containing:
        - vendor: GPU vendor name (str or None)
        - model: GPU model name (str or None)
        - vram_total_gb: Total VRAM in GB (str or None)
        - vram_free_gb: Free VRAM in GB (str or None)
        - driver_version: Driver version (str or None)
        - cuda_version: CUDA version (str or None)
        - compute_capability: CUDA compute capability (str or None)
    """
    gpus: List[Dict[str, Optional[str]]] = []

    # Try each GPU vendor detection method
    nvidia_gpus = _detect_nvidia_gpus()
    if nvidia_gpus:
        gpus.extend(nvidia_gpus)

    amd_gpus = _detect_amd_gpus()
    if amd_gpus:
        gpus.extend(amd_gpus)

    apple_gpus = _detect_apple_gpus()
    if apple_gpus:
        gpus.extend(apple_gpus)

    intel_gpus = _detect_intel_gpus()
    if intel_gpus:
        gpus.extend(intel_gpus)

    return gpus


def _run_command(
    cmd: List[str],
    timeout: float = 10,
) -> Optional[str]:
    """
    Run a subprocess command and return stdout.

    Args:
        cmd: Command and arguments as a list.
        timeout: Maximum time to wait for the command.

    Returns:
        Stdout string if successful, None otherwise.
    """
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=timeout,
        )
        if result.returncode == 0:
            return result.stdout.strip()
    except (subprocess.TimeoutExpired, FileNotFoundError, OSError):
        pass
    return None


def _detect_nvidia_gpus() -> List[Dict[str, Optional[str]]]:
    """Detect NVIDIA GPUs using nvidia-smi."""
    gpus: List[Dict[str, Optional[str]]] = []

    output = _run_command(["nvidia-smi", "--query-gpu=index,name,memory.total,memory.free,driver_version", "--format=csv,noheader,nounits"])
    if not output:
        return gpus

    # Get CUDA version
    cuda_output = _run_command(["nvidia-smi", "--query-gpu=driver_version", "--format=csv,noheader"])
    cuda_version = None
    cuda_query = _run_command(["nvidia-smi"])
    if cuda_query:
        match = re.search(r"CUDA Version:\s*(\S+)", cuda_query)
        if match:
            cuda_version = match.group(1)

    for line in output.splitlines():
        line = line.strip()
        if not line:
            continue
        parts = [p.strip() for p in line.split(",")]
        if len(parts) >= 5:
            gpu_info: Dict[str, Optional[str]] = {
                "vendor": "NVIDIA",
                "model": parts[1] if len(parts) > 1 else None,
                "vram_total_gb": _parse_memory_gb(parts[2]) if len(parts) > 2 else None,
                "vram_free_gb": _parse_memory_gb(parts[3]) if len(parts) > 3 else None,
                "driver_version": parts[4] if len(parts) > 4 else None,
                "cuda_version": cuda_version,
                "compute_capability": None,
            }

            # Try to get compute capability
            gpu_index = parts[0]
            cc_output = _run_command(
                ["nvidia-smi", "--query-gpu=compute_cap", "--id=" + gpu_index, "--format=csv,noheader"]
            )
            if cc_output:
                gpu_info["compute_capability"] = cc_output.strip()

            gpus.append(gpu_info)

    return gpus


def _detect_amd_gpus() -> List[Dict[str, Optional[str]]]:
    """Detect AMD GPUs using rocm-smi or lspci."""
    gpus: List[Dict[str, Optional[str]]] = []

    # Try rocm-smi first
    output = _run_command(["rocm-smi", "--showproductname", "--json"])
    if output:
        try:
            data = json.loads(output)
            # rocm-smi JSON structure varies by version
            if isinstance(data, dict):
                for card_key, card_data in data.items():
                    if isinstance(card_data, dict):
                        model = card_data.get("card_model", None) or card_data.get("card_series", None)
                        vram = card_data.get("vram_total", None)
                        if model:
                            gpu_info: Dict[str, Optional[str]] = {
                                "vendor": "AMD",
                                "model": str(model),
                                "vram_total_gb": _parse_memory_gb(str(vram)) if vram else None,
                                "vram_free_gb": None,
                                "driver_version": None,
                                "cuda_version": None,
                                "compute_capability": None,
                            }
                            gpus.append(gpu_info)
        except (json.JSONDecodeError, TypeError):
            pass

    # Fallback to lspci
    if not gpus:
        output = _run_command(["lspci"])
        if output:
            for line in output.splitlines():
                if "VGA" in line or "3D" in line or "Display" in line:
                    if "AMD" in line or "Radeon" in line or "Advanced Micro Devices" in line:
                        # Extract model name
                        model_match = re.search(r"(?:AMD|ATI|Radeon|Advanced Micro Devices)\s*[^\[]*", line)
                        model = model_match.group(0).strip() if model_match else None
                        gpu_info: Dict[str, Optional[str]] = {
                            "vendor": "AMD",
                            "model": model,
                            "vram_total_gb": None,
                            "vram_free_gb": None,
                            "driver_version": None,
                            "cuda_version": None,
                            "compute_capability": None,
                        }
                        gpus.append(gpu_info)

    return gpus


def _detect_apple_gpus() -> List[Dict[str, Optional[str]]]:
    """Detect Apple Silicon GPUs using system_profiler."""
    gpus: List[Dict[str, Optional[str]]] = []

    if platform.system() != "Darwin":
        return gpus

    output = _run_command(["system_profiler", "SPDisplaysDataType", "-json"])
    if not output:
        return gpus

    try:
        data = json.loads(output)
        displays = data.get("SPDisplaysDataType", [])
        for display in displays:
            chip = display.get("chipset-model", "")
            # Apple Silicon GPUs
            if "Apple" in chip or "M1" in chip or "M2" in chip or "M3" in chip or "M4" in chip:
                vram_total = display.get("vram", display.get("pci-vram", None))
                gpu_info: Dict[str, Optional[str]] = {
                    "vendor": "Apple Silicon",
                    "model": chip,
                    "vram_total_gb": _parse_memory_gb(str(vram_total)) if vram_total else None,
                    "vram_free_gb": None,
                    "driver_version": None,
                    "cuda_version": None,
                    "compute_capability": None,
                }
                gpus.append(gpu_info)
    except (json.JSONDecodeError, TypeError):
        pass

    return gpus


def _detect_intel_gpus() -> List[Dict[str, Optional[str]]]:
    """Detect Intel Arc GPUs using intel_gpu_top or lspci."""
    gpus: List[Dict[str, Optional[str]]] = []

    # Try intel_gpu_top
    output = _run_command(["intel_gpu_top", "-l"], timeout=3)
    if output and "Intel" in output:
        gpu_info: Dict[str, Optional[str]] = {
            "vendor": "Intel Arc",
            "model": None,
            "vram_total_gb": None,
            "vram_free_gb": None,
            "driver_version": None,
            "cuda_version": None,
            "compute_capability": None,
        }
        # Try to extract model
        model_match = re.search(r"(?:Intel|Arc)\s+\w+\s+\w+", output)
        if model_match:
            gpu_info["model"] = model_match.group(0).strip()
        gpus.append(gpu_info)
        return gpus

    # Fallback to lspci
    output = _run_command(["lspci"])
    if output:
        for line in output.splitlines():
            if "VGA" in line or "3D" in line or "Display" in line:
                if "Intel" in line and ("Arc" in line or "Iris" in line or "UHD" in line):
                    model_match = re.search(r"Intel\s+[^\[]*", line)
                    model = model_match.group(0).strip() if model_match else None
                    gpu_info: Dict[str, Optional[str]] = {
                        "vendor": "Intel Arc",
                        "model": model,
                        "vram_total_gb": None,
                        "vram_free_gb": None,
                        "driver_version": None,
                        "cuda_version": None,
                        "compute_capability": None,
                    }
                    gpus.append(gpu_info)

    return gpus


def _parse_memory_gb(value: str) -> Optional[str]:
    """
    Parse a memory value string into GB.

    Handles formats like: "8192", "8192 MiB", "8 GB", "8192MB", etc.

    Args:
        value: Memory value string.

    Returns:
        String representation of memory in GB, or None if parsing fails.
    """
    if not value:
        return None

    value = value.strip().upper()

    # Remove common suffixes
    multipliers = {
        "TB": 1024,
        "TIB": 1024,
        "GB": 1,
        "GIB": 1,
        "MB": 1 / 1024,
        "MIB": 1 / 1024,
        "KB": 1 / (1024 * 1024),
        "KIB": 1 / (1024 * 1024),
    }

    for suffix, mult in multipliers.items():
        if value.endswith(suffix):
            num_str = value[: -len(suffix)].strip()
            try:
                mb = float(num_str)
                return f"{mb * mult:.1f}"
            except ValueError:
                return None

    # Try plain number (assume MiB)
    try:
        mb = float(value)
        return f"{mb / 1024:.1f}"
    except ValueError:
        return None
