"""
Constants and configuration for LLM Hardware Advisor.
"""

# Quantization precision levels in order of preference (most memory-efficient first)
QUANT_LEVELS = ["int4", "int8", "fp16"]

# Bytes per parameter for each quantization level
BYTES_PER_PARAM = {
    "fp16": 2,
    "int8": 1,
    "int4": 0.5,
}

# Bytes per token for KV cache estimation (approximate)
BYTES_PER_TOKEN = {
    "fp16": 2.0,
    "int8": 1.0,
    "int4": 0.5,
}

# Safety margin for VRAM estimation (percentage of VRAM to reserve)
VRAM_SAFETY_MARGIN = 0.1

# Minimum free VRAM to keep available (GB)
MIN_FREE_VRAM_GB = 0.5

# Model categories
CATEGORIES = ["general", "coding", "math", "reasoning", "chat"]

# Category display names (English)
CATEGORY_NAMES = {
    "general": "General Purpose",
    "coding": "Code Generation",
    "math": "Mathematics",
    "reasoning": "Reasoning",
    "chat": "Chat / Dialogue",
}

# Category display names (Chinese)
CATEGORY_NAMES_ZH = {
    "general": "通用",
    "coding": "代码生成",
    "math": "数学",
    "reasoning": "推理",
    "chat": "对话",
}

# Supported GPU vendors
GPU_VENDORS = ["NVIDIA", "AMD", "Apple Silicon", "Intel Arc"]

# Approximate number of transformer layers per billion parameters
# Used for context VRAM estimation
LAYERS_PER_BILLION_PARAMS = 2

# Default context length for VRAM estimation when not specified
DEFAULT_CONTEXT_LENGTH = 4096
