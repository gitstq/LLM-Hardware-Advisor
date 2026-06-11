"""
Tests for the hardware detection modules.
"""

import json
import os
import sys
from unittest.mock import patch

import pytest

# Add project root to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from llm_hardware_advisor.detector.cpu import detect_cpu
from llm_hardware_advisor.detector.gpu import (
    _detect_nvidia_gpus,
    _parse_memory_gb,
    detect_gpus,
)
from llm_hardware_advisor.detector.memory import detect_memory
from llm_hardware_advisor.detector.system import detect_system


class TestCPUDetection:
    """Tests for CPU detection module."""

    def test_detect_cpu_returns_dict(self) -> None:
        """Test that detect_cpu returns a dictionary with expected keys."""
        result = detect_cpu()
        assert isinstance(result, dict)
        assert "model" in result
        assert "architecture" in result
        assert "physical_cores" in result
        assert "logical_cores" in result
        assert "frequency_mhz" in result
        assert "vendor" in result

    def test_detect_cpu_architecture(self) -> None:
        """Test that architecture is detected."""
        result = detect_cpu()
        assert result["architecture"] is not None

    def test_detect_cpu_logical_cores(self) -> None:
        """Test that logical cores are detected."""
        result = detect_cpu()
        # Logical cores should be detected on most systems
        if result["logical_cores"] is not None:
            cores = int(result["logical_cores"])
            assert cores >= 1


class TestGPUDetection:
    """Tests for GPU detection module."""

    def test_detect_gpus_returns_list(self) -> None:
        """Test that detect_gpus returns a list."""
        result = detect_gpus()
        assert isinstance(result, list)

    def test_detect_gpus_entries_have_keys(self) -> None:
        """Test that GPU entries have expected keys."""
        result = detect_gpus()
        for gpu in result:
            assert "vendor" in gpu
            assert "model" in gpu
            assert "vram_total_gb" in gpu
            assert "vram_free_gb" in gpu

    def test_parse_memory_gb_mb(self) -> None:
        """Test parsing memory values in MB."""
        assert _parse_memory_gb("8192") == "8.0"
        assert _parse_memory_gb("4096") == "4.0"

    def test_parse_memory_gb_with_suffix(self) -> None:
        """Test parsing memory values with suffixes."""
        assert _parse_memory_gb("8 GB") == "8.0"
        assert _parse_memory_gb("16GiB") == "16.0"
        assert _parse_memory_gb("4 MB") == "0.0"

    def test_parse_memory_gb_none(self) -> None:
        """Test parsing None and empty string."""
        assert _parse_memory_gb("") is None
        assert _parse_memory_gb(None) is None  # type: ignore

    def test_parse_memory_gb_tb(self) -> None:
        """Test parsing TB values."""
        result = _parse_memory_gb("2 TB")
        assert result is not None
        assert float(result) == 2048.0


class TestMemoryDetection:
    """Tests for memory detection module."""

    def test_detect_memory_returns_dict(self) -> None:
        """Test that detect_memory returns a dictionary."""
        result = detect_memory()
        assert isinstance(result, dict)
        assert "total_gb" in result
        assert "available_gb" in result
        assert "used_gb" in result

    def test_detect_memory_total(self) -> None:
        """Test that total memory is detected."""
        result = detect_memory()
        if result["total_gb"] is not None:
            total = float(result["total_gb"])
            assert total >= 0.5  # At least 512MB


class TestSystemDetection:
    """Tests for system detection module."""

    def test_detect_system_returns_dict(self) -> None:
        """Test that detect_system returns a dictionary."""
        result = detect_system()
        assert isinstance(result, dict)
        assert "os_name" in result
        assert "python_version" in result
        assert "architecture" in result

    def test_detect_system_os_name(self) -> None:
        """Test that OS name is detected."""
        result = detect_system()
        assert result["os_name"] is not None
        # On Linux, os_name may be overridden by distro name (e.g., "Ubuntu 22.04")
        # so we accept both the platform name and any non-empty string
        assert result["os_name"] is not None and len(result["os_name"]) > 0

    def test_detect_system_python_version(self) -> None:
        """Test that Python version is detected."""
        result = detect_system()
        assert result["python_version"] is not None
        # Should match major.minor.micro
        parts = result["python_version"].split(".")
        assert len(parts) == 3
