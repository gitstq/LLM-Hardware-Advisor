"""
Tests for the recommendation engine module.
"""

import json
import os
import sys
from typing import Dict, List, Optional

import pytest

# Add project root to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from llm_hardware_advisor.advisor.engine import (
    AdvisorEngine,
    HardwareProfile,
    ModelInfo,
    Recommendation,
)


def _make_hardware(
    gpu_vram: float = 8.0,
    ram: float = 16.0,
    has_gpu: bool = True,
    gpu_count: int = 1,
) -> HardwareProfile:
    """Create a mock HardwareProfile for testing."""
    gpus: List[Dict[str, Optional[str]]] = []
    if has_gpu:
        for _ in range(gpu_count):
            gpus.append({
                "vendor": "NVIDIA",
                "model": "Test GPU",
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


class TestAdvisorEngine:
    """Tests for the AdvisorEngine class."""

    def test_engine_loads_database(self) -> None:
        """Test that the engine loads models from the database."""
        engine = AdvisorEngine()
        assert len(engine.models) > 0

    def test_engine_has_minimum_models(self) -> None:
        """Test that the database has at least 50 models."""
        engine = AdvisorEngine()
        assert len(engine.models) >= 50

    def test_get_all_models(self) -> None:
        """Test get_all_models returns all models."""
        engine = AdvisorEngine()
        models = engine.get_all_models()
        assert len(models) == len(engine.models)

    def test_get_models_by_category(self) -> None:
        """Test filtering models by category."""
        engine = AdvisorEngine()
        coding_models = engine.get_models_by_category("coding")
        assert len(coding_models) > 0
        for model in coding_models:
            assert model.category == "coding"

    def test_get_models_by_category_empty(self) -> None:
        """Test filtering by non-existent category returns empty list."""
        engine = AdvisorEngine()
        models = engine.get_models_by_category("nonexistent")
        assert len(models) == 0

    def test_find_model_by_name(self) -> None:
        """Test finding a model by name."""
        engine = AdvisorEngine()
        model = engine.find_model_by_name("Llama 3.1 8B")
        assert model is not None
        assert "Llama 3.1" in model.name

    def test_find_model_by_name_not_found(self) -> None:
        """Test finding a non-existent model returns None."""
        engine = AdvisorEngine()
        model = engine.find_model_by_name("NonExistentModel")
        assert model is None

    def test_find_model_by_name_case_insensitive(self) -> None:
        """Test that model search is case-insensitive."""
        engine = AdvisorEngine()
        model = engine.find_model_by_name("llama 3.1 8b")
        assert model is not None


class TestVRAMEstimation:
    """Tests for VRAM estimation."""

    def test_estimate_vram_int4(self) -> None:
        """Test VRAM estimation for INT4 quantization."""
        engine = AdvisorEngine()
        model = engine.find_model_by_name("Llama 3.1 8B")
        assert model is not None
        vram = engine.estimate_vram(model, "int4")
        assert vram > 0
        assert vram < 20  # Should be reasonable for 8B INT4

    def test_estimate_vram_fp16(self) -> None:
        """Test VRAM estimation for FP16 quantization."""
        engine = AdvisorEngine()
        model = engine.find_model_by_name("Llama 3.1 8B")
        assert model is not None
        vram = engine.estimate_vram(model, "fp16")
        assert vram > 0
        # FP16 should be roughly 2x INT4
        vram_int4 = engine.estimate_vram(model, "int4")
        assert vram > vram_int4

    def test_estimate_vram_int4_less_than_fp16(self) -> None:
        """Test that INT4 always requires less VRAM than FP16."""
        engine = AdvisorEngine()
        for model in engine.models[:10]:
            vram_int4 = engine.estimate_vram(model, "int4")
            vram_fp16 = engine.estimate_vram(model, "fp16")
            assert vram_int4 < vram_fp16


class TestRecommendations:
    """Tests for the recommendation logic."""

    def test_recommend_returns_list(self) -> None:
        """Test that recommend returns a list of Recommendations."""
        engine = AdvisorEngine()
        hardware = _make_hardware(gpu_vram=8.0, ram=16.0)
        recs = engine.recommend(hardware)
        assert isinstance(recs, list)

    def test_recommend_with_small_gpu(self) -> None:
        """Test recommendations with a small GPU (4GB)."""
        engine = AdvisorEngine()
        hardware = _make_hardware(gpu_vram=4.0, ram=8.0)
        recs = engine.recommend(hardware)
        # Should find at least some lightweight models
        assert len(recs) > 0

    def test_recommend_with_large_gpu(self) -> None:
        """Test recommendations with a large GPU (24GB)."""
        engine = AdvisorEngine()
        hardware = _make_hardware(gpu_vram=24.0, ram=32.0)
        recs = engine.recommend(hardware)
        assert len(recs) > 0
        # Should include larger models
        model_names = [r.model.name for r in recs]
        has_large = any("7B" in n or "8B" in n or "14B" in n for n in model_names)
        assert has_large

    def test_recommend_with_no_gpu(self) -> None:
        """Test recommendations with no GPU (CPU only)."""
        engine = AdvisorEngine()
        hardware = _make_hardware(has_gpu=False, ram=16.0)
        recs = engine.recommend(hardware)
        assert len(recs) > 0
        # All should be CPU-only
        for rec in recs:
            assert rec.can_run_on_cpu

    def test_recommend_sorted_by_score(self) -> None:
        """Test that recommendations are sorted by fitness score."""
        engine = AdvisorEngine()
        hardware = _make_hardware(gpu_vram=16.0, ram=32.0)
        recs = engine.recommend(hardware)
        if len(recs) > 1:
            for i in range(len(recs) - 1):
                assert recs[i].fitness_score >= recs[i + 1].fitness_score

    def test_recommend_with_category_filter(self) -> None:
        """Test category filtering in recommendations."""
        engine = AdvisorEngine()
        hardware = _make_hardware(gpu_vram=8.0, ram=16.0)
        recs = engine.recommend(hardware, category="coding")
        for rec in recs:
            assert rec.model.category == "coding"

    def test_recommend_top_n(self) -> None:
        """Test limiting number of recommendations."""
        engine = AdvisorEngine()
        hardware = _make_hardware(gpu_vram=16.0, ram=32.0)
        recs = engine.recommend(hardware, top_n=3)
        assert len(recs) <= 3

    def test_recommendation_has_commands(self) -> None:
        """Test that each recommendation has run commands."""
        engine = AdvisorEngine()
        hardware = _make_hardware(gpu_vram=8.0, ram=16.0)
        recs = engine.recommend(hardware)
        for rec in recs:
            assert "ollama" in rec.run_commands
            assert "llama.cpp" in rec.run_commands
            assert "download" in rec.run_commands

    def test_recommendation_fitness_range(self) -> None:
        """Test that fitness scores are in valid range."""
        engine = AdvisorEngine()
        hardware = _make_hardware(gpu_vram=8.0, ram=16.0)
        recs = engine.recommend(hardware)
        for rec in recs:
            assert 0 <= rec.fitness_score <= 100


class TestModelComparison:
    """Tests for model comparison."""

    def test_compare_existing_models(self) -> None:
        """Test comparing two existing models."""
        engine = AdvisorEngine()
        result = engine.compare_models("Llama 3.1 8B", "Mistral 7B")
        assert "model1" in result
        assert "model2" in result
        assert "error" not in result

    def test_compare_nonexistent_model(self) -> None:
        """Test comparing with a non-existent model."""
        engine = AdvisorEngine()
        result = engine.compare_models("NonExistent", "Llama 3.1 8B")
        assert "error" in result

    def test_compare_vram_estimates(self) -> None:
        """Test that comparison includes VRAM estimates."""
        engine = AdvisorEngine()
        result = engine.compare_models("Llama 3.1 8B", "Mistral 7B")
        if "error" not in result:
            assert "vram_estimates" in result["model1"]
            assert "vram_estimates" in result["model2"]
            assert "int4" in result["model1"]["vram_estimates"]

    def test_compare_with_hardware(self) -> None:
        """Test comparison with hardware for fitness scoring."""
        engine = AdvisorEngine()
        hardware = _make_hardware(gpu_vram=8.0, ram=16.0)
        result = engine.compare_models("Llama 3.1 8B", "Mistral 7B", hardware=hardware)
        if "error" not in result:
            assert "fitness_score" in result["model1"]
            assert "fitness_score" in result["model2"]


class TestHardwareProfile:
    """Tests for HardwareProfile."""

    def test_total_vram_single_gpu(self) -> None:
        """Test total VRAM with a single GPU."""
        hw = _make_hardware(gpu_vram=8.0)
        assert hw.total_vram_gb == 8.0

    def test_total_vram_multi_gpu(self) -> None:
        """Test total VRAM with multiple GPUs."""
        hw = _make_hardware(gpu_vram=8.0, gpu_count=2)
        assert hw.total_vram_gb == 16.0

    def test_max_single_gpu_vram(self) -> None:
        """Test max single GPU VRAM."""
        hw = _make_hardware(gpu_vram=8.0, gpu_count=2)
        assert hw.max_single_gpu_vram_gb == 8.0

    def test_has_gpu(self) -> None:
        """Test has_gpu property."""
        hw_with = _make_hardware(has_gpu=True)
        hw_without = _make_hardware(has_gpu=False)
        assert hw_with.has_gpu is True
        assert hw_without.has_gpu is False

    def test_gpu_vendor(self) -> None:
        """Test GPU vendor property."""
        hw = _make_hardware()
        assert hw.gpu_vendor == "NVIDIA"

    def test_gpu_vendor_no_gpu(self) -> None:
        """Test GPU vendor with no GPU."""
        hw = _make_hardware(has_gpu=False)
        assert hw.gpu_vendor is None

    def test_total_ram(self) -> None:
        """Test total RAM."""
        hw = _make_hardware(ram=32.0)
        assert hw.total_ram_gb == 32.0
