"""
Recommendation engine for LLM Hardware Advisor.

Core logic for matching hardware capabilities with LLM model requirements.
Considers GPU VRAM, system RAM, quantization levels, context length impact,
and generates ranked recommendations with usage commands.
"""

import json
import os
from typing import Any, Dict, List, Optional, Tuple

from ..utils.constants import (
    BYTES_PER_PARAM,
    BYTES_PER_TOKEN,
    CATEGORIES,
    LAYERS_PER_BILLION_PARAMS,
    MIN_FREE_VRAM_GB,
    QUANT_LEVELS,
    VRAM_SAFETY_MARGIN,
)


class HardwareProfile:
    """Represents detected hardware capabilities."""

    def __init__(
        self,
        cpu: Dict[str, Optional[str]],
        gpus: List[Dict[str, Optional[str]]],
        memory: Dict[str, Optional[str]],
        system: Dict[str, Optional[str]],
    ) -> None:
        """
        Initialize a HardwareProfile.

        Args:
            cpu: CPU information dictionary.
            gpus: List of GPU information dictionaries.
            memory: Memory information dictionary.
            system: System information dictionary.
        """
        self.cpu = cpu
        self.gpus = gpus
        self.memory = memory
        self.system = system

    @property
    def total_vram_gb(self) -> float:
        """Total GPU VRAM across all GPUs in GB."""
        total = 0.0
        for gpu in self.gpus:
            vram = gpu.get("vram_total_gb")
            if vram:
                try:
                    total += float(vram)
                except (ValueError, TypeError):
                    pass
        return total

    @property
    def max_single_gpu_vram_gb(self) -> float:
        """VRAM of the single largest GPU in GB."""
        max_vram = 0.0
        for gpu in self.gpus:
            vram = gpu.get("vram_total_gb")
            if vram:
                try:
                    max_vram = max(max_vram, float(vram))
                except (ValueError, TypeError):
                    pass
        return max_vram

    @property
    def total_ram_gb(self) -> float:
        """Total system RAM in GB."""
        total = self.memory.get("total_gb")
        if total:
            try:
                return float(total)
            except (ValueError, TypeError):
                pass
        return 0.0

    @property
    def has_gpu(self) -> bool:
        """Whether any GPU was detected."""
        return len(self.gpus) > 0

    @property
    def gpu_vendor(self) -> Optional[str]:
        """Primary GPU vendor."""
        if self.gpus:
            return self.gpus[0].get("vendor")
        return None

    @property
    def gpu_count(self) -> int:
        """Number of GPUs detected."""
        return len(self.gpus)


class ModelInfo:
    """Represents a model in the database."""

    def __init__(self, data: Dict[str, Any]) -> None:
        """
        Initialize a ModelInfo from a database entry.

        Args:
            data: Model data dictionary from models.json.
        """
        self.name: str = data.get("name", "Unknown")
        self.provider: str = data.get("provider", "Unknown")
        self.parameter_count: str = data.get("parameter_count", "Unknown")
        self.param_billions: float = data.get("param_billions", 0)
        self.context_length: int = data.get("context_length", 4096)
        self.vram_requirements: Dict[str, float] = data.get("vram_requirements", {})
        self.quantization: List[str] = data.get("quantization", [])
        self.category: str = data.get("category", "general")
        self.license: str = data.get("license", "Unknown")
        self.huggingface_id: str = data.get("huggingface_id", "")
        self.tags: List[str] = data.get("tags", [])
        self.active_params: Optional[float] = data.get("active_params", None)


class Recommendation:
    """Represents a single model recommendation."""

    def __init__(
        self,
        model: ModelInfo,
        quant_level: str,
        estimated_vram_gb: float,
        fitness_score: float,
        can_run_on_gpu: bool,
        can_run_on_cpu: bool,
        run_commands: Dict[str, str],
    ) -> None:
        """
        Initialize a Recommendation.

        Args:
            model: The recommended model.
            quant_level: Recommended quantization level.
            estimated_vram_gb: Estimated VRAM needed in GB.
            fitness_score: Fitness score (0-100).
            can_run_on_gpu: Whether it can run on the detected GPU.
            can_run_on_cpu: Whether it can run on CPU (offloaded).
            run_commands: Dictionary of run commands (e.g., ollama, llama.cpp).
        """
        self.model = model
        self.quant_level = quant_level
        self.estimated_vram_gb = estimated_vram_gb
        self.fitness_score = fitness_score
        self.can_run_on_gpu = can_run_on_gpu
        self.can_run_on_cpu = can_run_on_cpu
        self.run_commands = run_commands


class AdvisorEngine:
    """Core recommendation engine."""

    def __init__(self) -> None:
        """Initialize the advisor engine and load the model database."""
        self.models: List[ModelInfo] = []
        self._load_database()

    def _load_database(self) -> None:
        """Load models from the built-in JSON database."""
        db_path = os.path.join(os.path.dirname(__file__), "..", "database", "models.json")
        db_path = os.path.normpath(db_path)

        if not os.path.exists(db_path):
            return

        try:
            with open(db_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            for entry in data:
                self.models.append(ModelInfo(entry))
        except (json.JSONDecodeError, OSError) as e:
            # Silently fail - the engine will work with an empty model list
            pass

    def get_all_models(self) -> List[ModelInfo]:
        """Return all models in the database."""
        return list(self.models)

    def get_models_by_category(self, category: str) -> List[ModelInfo]:
        """
        Return models filtered by category.

        Args:
            category: Category name (general, coding, math, reasoning, chat).

        Returns:
            List of matching models.
        """
        return [m for m in self.models if m.category == category]

    def find_model_by_name(self, name: str) -> Optional[ModelInfo]:
        """
        Find a model by name (case-insensitive partial match).

        Args:
            name: Model name to search for.

        Returns:
            First matching ModelInfo or None.
        """
        name_lower = name.lower()
        for model in self.models:
            if name_lower in model.name.lower():
                return model
        return None

    def estimate_vram(
        self,
        model: ModelInfo,
        quant_level: str,
        context_length: Optional[int] = None,
    ) -> float:
        """
        Estimate VRAM needed for a model with given quantization and context.

        Formula:
            model_vram = param_billions * bytes_per_param[quant]
            context_vram = context_length * bytes_per_token[quant] * num_layers
            total_vram = model_vram + context_vram + safety_overhead

        Args:
            model: The model to estimate for.
            quant_level: Quantization level (int4, int8, fp16).
            context_length: Context length to account for. Uses model default if None.

        Returns:
            Estimated VRAM in GB.
        """
        if context_length is None:
            context_length = model.context_length

        # Use active params for MoE models if available
        effective_params = model.active_params if model.active_params else model.param_billions

        # Model weights VRAM
        bytes_per_param = BYTES_PER_PARAM.get(quant_level, BYTES_PER_PARAM["fp16"])
        model_vram_gb = effective_params * bytes_per_param

        # KV cache estimation for context
        bytes_per_token = BYTES_PER_TOKEN.get(quant_level, BYTES_PER_TOKEN["fp16"])
        num_layers = max(1, int(effective_params * LAYERS_PER_BILLION_PARAMS))
        context_vram_gb = (context_length * bytes_per_token * num_layers) / (1024 ** 3)

        # Safety overhead (10%)
        safety_overhead = model_vram_gb * VRAM_SAFETY_MARGIN

        total_vram = model_vram_gb + context_vram_gb + safety_overhead

        return round(total_vram, 2)

    def recommend(
        self,
        hardware: HardwareProfile,
        category: Optional[str] = None,
        top_n: int = 10,
    ) -> List[Recommendation]:
        """
        Generate model recommendations based on hardware profile.

        Args:
            hardware: Detected hardware profile.
            category: Optional category filter.
            top_n: Maximum number of recommendations to return.

        Returns:
            List of Recommendation objects sorted by fitness score (descending).
        """
        candidates = self.models

        # Filter by category if specified
        if category and category in CATEGORIES:
            candidates = [m for m in candidates if m.category == category]

        recommendations: List[Recommendation] = []

        for model in candidates:
            # Try each quantization level from most efficient to least
            for quant_level in QUANT_LEVELS:
                if quant_level not in model.vram_requirements:
                    continue

                estimated_vram = self.estimate_vram(model, quant_level)

                # Determine if it can run on GPU
                available_vram = hardware.max_single_gpu_vram_gb
                can_run_on_gpu = (
                    hardware.has_gpu
                    and estimated_vram <= available_vram - MIN_FREE_VRAM_GB
                )

                # Determine if it can run on CPU with system RAM
                # CPU offloading needs more RAM due to additional overhead
                cpu_ram_needed = estimated_vram * 1.5
                can_run_on_cpu = cpu_ram_needed <= hardware.total_ram_gb

                if not can_run_on_gpu and not can_run_on_cpu:
                    continue

                # Calculate fitness score
                fitness = self._calculate_fitness(
                    model=model,
                    quant_level=quant_level,
                    estimated_vram=estimated_vram,
                    hardware=hardware,
                    can_run_on_gpu=can_run_on_gpu,
                )

                # Generate run commands
                commands = self._generate_run_commands(model, quant_level)

                rec = Recommendation(
                    model=model,
                    quant_level=quant_level,
                    estimated_vram_gb=estimated_vram,
                    fitness_score=fitness,
                    can_run_on_gpu=can_run_on_gpu,
                    can_run_on_cpu=can_run_on_cpu,
                    run_commands=commands,
                )
                recommendations.append(rec)

                # Only recommend the best quantization for each model
                break

        # Sort by fitness score descending
        recommendations.sort(key=lambda r: r.fitness_score, reverse=True)

        return recommendations[:top_n]

    def _calculate_fitness(
        self,
        model: ModelInfo,
        quant_level: str,
        estimated_vram: float,
        hardware: HardwareProfile,
        can_run_on_gpu: bool,
    ) -> float:
        """
        Calculate a fitness score (0-100) for a model recommendation.

        Scoring factors:
        - Larger models get higher scores (more capable)
        - GPU-native running preferred over CPU offloading
        - Better quantization preferred (higher precision)
        - Models that use hardware resources efficiently score higher
        - Tagged "recommended" or "popular" get bonus points

        Args:
            model: The model being scored.
            quant_level: Recommended quantization level.
            estimated_vram: Estimated VRAM needed.
            hardware: Hardware profile.
            can_run_on_gpu: Whether it runs natively on GPU.

        Returns:
            Fitness score from 0 to 100.
        """
        score = 0.0

        # Factor 1: Model capability (based on parameter count) - 30 points max
        if model.active_params:
            # MoE models: score based on active params
            param_score = min(30, model.active_params * 0.5)
        else:
            param_score = min(30, model.param_billions * 0.5)
        score += param_score

        # Factor 2: GPU native bonus - 25 points
        if can_run_on_gpu:
            score += 25
        else:
            score += 5  # CPU offloading is possible but less ideal

        # Factor 3: Quantization quality - 15 points max
        quant_scores = {"fp16": 15, "int8": 10, "int4": 5}
        score += quant_scores.get(quant_level, 5)

        # Factor 4: Resource utilization efficiency - 15 points max
        if hardware.has_gpu and can_run_on_gpu:
            available_vram = hardware.max_single_gpu_vram_gb
            if available_vram > 0:
                utilization = estimated_vram / available_vram
                # Sweet spot: using 50-80% of available VRAM
                if 0.5 <= utilization <= 0.8:
                    score += 15
                elif 0.3 <= utilization < 0.5:
                    score += 10
                elif 0.8 < utilization <= 0.95:
                    score += 8
                elif utilization < 0.3:
                    score += 5
                else:
                    score += 3
        else:
            score += 5

        # Factor 5: Tag bonuses - 15 points max
        if "recommended" in model.tags:
            score += 8
        if "popular" in model.tags:
            score += 5
        if "flagship" in model.tags:
            score += 2

        return round(min(100, score), 1)

    def _generate_run_commands(
        self,
        model: ModelInfo,
        quant_level: str,
    ) -> Dict[str, str]:
        """
        Generate run commands for a model recommendation.

        Args:
            model: The model to generate commands for.
            quant_level: Recommended quantization level.

        Returns:
            Dictionary with command types as keys and commands as values.
        """
        commands: Dict[str, str] = {}

        # Ollama command
        # Convert huggingface_id to ollama model name format
        ollama_name = model.huggingface_id.split("/")[-1].lower().replace("-", ":")
        # Try to infer a reasonable ollama tag
        quant_tag = "q4" if quant_level == "int4" else ("q8" if quant_level == "int8" else "fp16")
        commands["ollama"] = f"ollama run {model.huggingface_id.split('/')[1]}:{quant_tag}"

        # llama.cpp command
        gguf_quant = "Q4_K_M" if quant_level == "int4" else ("Q8_0" if quant_level == "int8" else "F16")
        commands["llama.cpp"] = (
            f"./llama-server -m {model.huggingface_id.split('/')[-1]}-{gguf_quant}.gguf "
            f"-c {model.context_length} -ngl 99"
        )

        # HuggingFace download hint
        commands["download"] = (
            f"huggingface-cli download {model.huggingface_id}"
        )

        return commands

    def compare_models(
        self,
        name1: str,
        name2: str,
        hardware: Optional[HardwareProfile] = None,
    ) -> Dict[str, Any]:
        """
        Compare two models side by side.

        Args:
            name1: First model name.
            name2: Second model name.
            hardware: Optional hardware profile for fitness comparison.

        Returns:
            Comparison dictionary with details for both models.
        """
        model1 = self.find_model_by_name(name1)
        model2 = self.find_model_by_name(name2)

        if not model1 and not model2:
            return {"error": f"Neither '{name1}' nor '{name2}' found in database."}
        if not model1:
            return {"error": f"Model '{name1}' not found in database."}
        if not model2:
            return {"error": f"Model '{name2}' not found in database."}

        comparison: Dict[str, Any] = {
            "model1": self._model_to_dict(model1),
            "model2": self._model_to_dict(model2),
        }

        # Add VRAM estimates for each quantization level
        for label, model in [("model1", model1), ("model2", model2)]:
            vram_estimates: Dict[str, float] = {}
            for quant in QUANT_LEVELS:
                if quant in model.vram_requirements:
                    vram_estimates[quant] = self.estimate_vram(model, quant)
            comparison[label]["vram_estimates"] = vram_estimates

        # Add fitness scores if hardware is provided
        if hardware:
            for label, model in [("model1", model1), ("model2", model2)]:
                best_fitness = 0.0
                best_quant = None
                for quant in QUANT_LEVELS:
                    if quant in model.vram_requirements:
                        est = self.estimate_vram(model, quant)
                        available = hardware.max_single_gpu_vram_gb
                        can_gpu = hardware.has_gpu and est <= available - MIN_FREE_VRAM_GB
                        fitness = self._calculate_fitness(
                            model, quant, est, hardware, can_gpu
                        )
                        if fitness > best_fitness:
                            best_fitness = fitness
                            best_quant = quant
                comparison[label]["fitness_score"] = best_fitness
                comparison[label]["recommended_quant"] = best_quant

        return comparison

    def _model_to_dict(self, model: ModelInfo) -> Dict[str, Any]:
        """Convert a ModelInfo to a plain dictionary for serialization."""
        return {
            "name": model.name,
            "provider": model.provider,
            "parameter_count": model.parameter_count,
            "param_billions": model.param_billions,
            "context_length": model.context_length,
            "vram_requirements": model.vram_requirements,
            "quantization": model.quantization,
            "category": model.category,
            "license": model.license,
            "huggingface_id": model.huggingface_id,
            "tags": model.tags,
            "active_params": model.active_params,
        }
