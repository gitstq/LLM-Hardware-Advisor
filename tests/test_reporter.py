"""
Tests for the report formatter module.
"""

import json
import os
import sys
from typing import Dict, List, Optional

import pytest

# Add project root to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from llm_hardware_advisor.advisor.engine import (
    HardwareProfile,
    Recommendation,
)
from llm_hardware_advisor.reporter.formatter import ReportFormatter


def _make_hardware(
    gpu_vram: float = 8.0,
    ram: float = 16.0,
    has_gpu: bool = True,
) -> HardwareProfile:
    """Create a mock HardwareProfile for testing."""
    gpus: List[Dict[str, Optional[str]]] = []
    if has_gpu:
        gpus.append({
            "vendor": "NVIDIA",
            "model": "RTX 4070",
            "vram_total_gb": str(gpu_vram),
            "vram_free_gb": str(gpu_vram * 0.8),
            "driver_version": "1.0",
            "cuda_version": "12.0",
            "compute_capability": "8.6",
        })

    return HardwareProfile(
        cpu={
            "model": "Test CPU",
            "architecture": "x86_64",
            "physical_cores": "8",
            "logical_cores": "16",
            "frequency_mhz": "3600",
            "vendor": "Test",
        },
        gpus=gpus,
        memory={
            "total_gb": str(ram),
            "available_gb": str(ram * 0.7),
            "used_gb": str(ram * 0.3),
            "percent_used": "30.0",
        },
        system={
            "os_name": "Linux",
            "os_version": "1.0",
            "python_version": "3.11.0",
            "disk_free_gb": "100.0",
        },
    )


def _make_recommendation(
    name: str = "Test Model",
    score: float = 75.0,
    vram: float = 5.0,
    gpu: bool = True,
) -> Recommendation:
    """Create a mock Recommendation for testing."""
    from llm_hardware_advisor.advisor.engine import ModelInfo

    model_data = {
        "name": name,
        "provider": "Test Provider",
        "parameter_count": "7B",
        "param_billions": 7,
        "context_length": 8192,
        "vram_requirements": {"fp16": 14, "int8": 8, "int4": 5},
        "quantization": ["GGUF/INT4", "GGUF/INT8", "FP16"],
        "category": "general",
        "license": "MIT",
        "huggingface_id": "test/model",
        "tags": ["popular"],
    }
    model = ModelInfo(model_data)

    return Recommendation(
        model=model,
        quant_level="int4",
        estimated_vram_gb=vram,
        fitness_score=score,
        can_run_on_gpu=gpu,
        can_run_on_cpu=True,
        run_commands={
            "ollama": f"ollama run {name}:q4",
            "llama.cpp": f"./llama-server -m {name}-Q4_K_M.gguf",
            "download": f"huggingface-cli download test/{name}",
        },
    )


class TestFormatterHardware:
    """Tests for hardware report formatting."""

    def test_format_hardware_terminal(self) -> None:
        """Test terminal format for hardware detection."""
        formatter = ReportFormatter(lang="en")
        hardware = _make_hardware()
        output = formatter.format_hardware_detection(hardware, fmt="terminal")
        assert isinstance(output, str)
        assert len(output) > 0
        assert "CPU" in output
        assert "GPU" in output
        assert "Memory" in output

    def test_format_hardware_terminal_zh(self) -> None:
        """Test Chinese terminal format for hardware detection."""
        formatter = ReportFormatter(lang="zh")
        hardware = _make_hardware()
        output = formatter.format_hardware_detection(hardware, fmt="terminal")
        assert isinstance(output, str)
        assert len(output) > 0

    def test_format_hardware_json(self) -> None:
        """Test JSON format for hardware detection."""
        formatter = ReportFormatter(lang="en")
        hardware = _make_hardware()
        output = formatter.format_hardware_detection(hardware, fmt="json")
        assert isinstance(output, str)
        data = json.loads(output)
        assert "cpu" in data
        assert "gpus" in data
        assert "memory" in data
        assert "system" in data
        assert "summary" in data

    def test_format_hardware_markdown(self) -> None:
        """Test Markdown format for hardware detection."""
        formatter = ReportFormatter(lang="en")
        hardware = _make_hardware()
        output = formatter.format_hardware_detection(hardware, fmt="markdown")
        assert isinstance(output, str)
        assert "# Hardware Detection Report" in output
        assert "## CPU" in output
        assert "## GPU" in output

    def test_format_hardware_no_gpu(self) -> None:
        """Test hardware formatting with no GPU."""
        formatter = ReportFormatter(lang="en")
        hardware = _make_hardware(has_gpu=False)
        output = formatter.format_hardware_detection(hardware, fmt="terminal")
        assert "No GPU detected" in output


class TestFormatterRecommendations:
    """Tests for recommendation report formatting."""

    def test_format_recommendations_terminal(self) -> None:
        """Test terminal format for recommendations."""
        formatter = ReportFormatter(lang="en")
        hardware = _make_hardware()
        recs = [_make_recommendation("Model A", 80.0), _make_recommendation("Model B", 60.0)]
        output = formatter.format_recommendations(recs, hardware, fmt="terminal")
        assert isinstance(output, str)
        assert "Model A" in output
        assert "Model B" in output

    def test_format_recommendations_json(self) -> None:
        """Test JSON format for recommendations."""
        formatter = ReportFormatter(lang="en")
        hardware = _make_hardware()
        recs = [_make_recommendation()]
        output = formatter.format_recommendations(recs, hardware, fmt="json")
        data = json.loads(output)
        assert "recommendations" in data
        assert "hardware_summary" in data
        assert len(data["recommendations"]) == 1

    def test_format_recommendations_markdown(self) -> None:
        """Test Markdown format for recommendations."""
        formatter = ReportFormatter(lang="en")
        hardware = _make_hardware()
        recs = [_make_recommendation()]
        output = formatter.format_recommendations(recs, hardware, fmt="markdown")
        assert "# LLM Recommendations" in output
        assert "## Hardware Summary" in output

    def test_format_recommendations_empty(self) -> None:
        """Test formatting empty recommendations."""
        formatter = ReportFormatter(lang="en")
        hardware = _make_hardware()
        output = formatter.format_recommendations([], hardware, fmt="terminal")
        assert "No models found" in output


class TestFormatterModelList:
    """Tests for model list formatting."""

    def test_format_model_list_terminal(self) -> None:
        """Test terminal format for model list."""
        formatter = ReportFormatter(lang="en")
        from llm_hardware_advisor.advisor.engine import AdvisorEngine

        engine = AdvisorEngine()
        models = engine.get_all_models()[:5]
        output = formatter.format_model_list(models, fmt="terminal")
        assert isinstance(output, str)
        assert "All Models in Database" in output

    def test_format_model_list_json(self) -> None:
        """Test JSON format for model list."""
        formatter = ReportFormatter(lang="en")
        from llm_hardware_advisor.advisor.engine import AdvisorEngine

        engine = AdvisorEngine()
        models = engine.get_all_models()[:3]
        output = formatter.format_model_list(models, fmt="json")
        data = json.loads(output)
        assert isinstance(data, list)
        assert len(data) == 3

    def test_format_model_list_markdown(self) -> None:
        """Test Markdown format for model list."""
        formatter = ReportFormatter(lang="en")
        from llm_hardware_advisor.advisor.engine import AdvisorEngine

        engine = AdvisorEngine()
        models = engine.get_all_models()[:3]
        output = formatter.format_model_list(models, fmt="markdown")
        assert "# All Models" in output


class TestFormatterComparison:
    """Tests for comparison formatting."""

    def test_format_comparison_terminal(self) -> None:
        """Test terminal format for comparison."""
        formatter = ReportFormatter(lang="en")
        comparison = {
            "model1": {
                "name": "Model A",
                "provider": "Provider A",
                "parameter_count": "7B",
                "context_length": 8192,
                "category": "general",
                "license": "MIT",
                "vram_estimates": {"int4": 5.0, "int8": 8.0, "fp16": 14.0},
                "fitness_score": 75.0,
                "recommended_quant": "int4",
            },
            "model2": {
                "name": "Model B",
                "provider": "Provider B",
                "parameter_count": "13B",
                "context_length": 4096,
                "category": "general",
                "license": "Apache 2.0",
                "vram_estimates": {"int4": 8.0, "int8": 14.0, "fp16": 26.0},
                "fitness_score": 65.0,
                "recommended_quant": "int4",
            },
        }
        output = formatter.format_comparison(comparison, fmt="terminal")
        assert isinstance(output, str)
        assert "Model A" in output
        assert "Model B" in output

    def test_format_comparison_error(self) -> None:
        """Test comparison formatting with error."""
        formatter = ReportFormatter(lang="en")
        comparison = {"error": "Model not found"}
        output = formatter.format_comparison(comparison, fmt="terminal")
        assert "not found" in output

    def test_format_comparison_json(self) -> None:
        """Test JSON format for comparison."""
        formatter = ReportFormatter(lang="en")
        comparison = {
            "model1": {"name": "A", "vram_estimates": {"int4": 5.0}},
            "model2": {"name": "B", "vram_estimates": {"int4": 8.0}},
        }
        output = formatter.format_comparison(comparison, fmt="json")
        data = json.loads(output)
        assert "model1" in data

    def test_format_comparison_markdown(self) -> None:
        """Test Markdown format for comparison."""
        formatter = ReportFormatter(lang="en")
        comparison = {
            "model1": {
                "name": "Model A",
                "provider": "Provider A",
                "parameter_count": "7B",
                "context_length": 8192,
                "category": "general",
                "license": "MIT",
                "vram_estimates": {"int4": 5.0, "int8": 8.0, "fp16": 14.0},
            },
            "model2": {
                "name": "Model B",
                "provider": "Provider B",
                "parameter_count": "13B",
                "context_length": 4096,
                "category": "general",
                "license": "Apache 2.0",
                "vram_estimates": {"int4": 8.0, "int8": 14.0, "fp16": 26.0},
            },
        }
        output = formatter.format_comparison(comparison, fmt="markdown")
        assert "# Model Comparison" in output
