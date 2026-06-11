<div align="center">
  <img src="assets/logo.png" alt="LLM Hardware Advisor Logo" width="120" height="120">

# 🤖 LLM-Hardware-Advisor

**Detect your hardware. Find your perfect local LLM.**

[![Python 3.9+](https://img.shields.io/badge/python-3.9%2B-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Tests](https://img.shields.io/badge/tests-61%20passing-brightgreen.svg)]()
[![Models](https://img.shields.io/badge/models-66%2B-orange.svg)]()

**LLM-Hardware-Advisor** is a smart CLI tool that detects your system hardware (CPU, GPU, RAM, Disk) and recommends the best open-source Large Language Models you can run locally — with optimal quantization settings, context length estimates, and ready-to-use commands for Ollama and llama.cpp.

✨ **Supports NVIDIA, AMD, Apple Silicon, and Intel Arc GPUs.**

</div>

---

## ✨ Core Features

| Feature | Description |
|---------|-------------|
| 🖥️ **Hardware Detection** | Auto-detect CPU, GPU (NVIDIA/AMD/Apple Silicon/Intel Arc), RAM, Disk, OS |
| 🧠 **66+ Model Database** | Built-in database covering Llama, Qwen, DeepSeek, Mistral, Phi, Gemma, CodeLlama, and more |
| 📊 **Smart Scoring** | Fitness score (0-100) based on VRAM, quantization, and context length |
| 🔢 **Multi-Quantization** | INT4 / INT8 / FP16 strategy recommendations |
| 🌐 **Bilingual** | English and Chinese (中文) interface support |
| 📤 **Export** | Export reports to JSON or Markdown |
| 🚀 **Ready Commands** | Generated Ollama & llama.cpp launch commands |
| 🧪 **Well Tested** | 61 unit tests with full coverage |

## 🚀 Quick Start

### Installation

```bash
# Clone the repository
git clone https://github.com/gitstq/LLM-Hardware-Advisor.git
cd LLM-Hardware-Advisor

# Install dependencies
pip install -r requirements.txt

# Or install as a package
pip install .
```

### Usage

```bash
# Detect hardware only
llm-advisor detect

# Get LLM recommendations (default)
llm-advisor recommend

# Recommend with Chinese output
llm-advisor recommend --lang zh

# Filter by category
llm-advisor recommend --category coding
llm-advisor recommend --category general
llm-advisor recommend --category math

# Compare two models
llm-advisor compare "Llama 3.1 8B" "Qwen 2.5 7B"

# List all built-in models
llm-advisor list-models

# Export report
llm-advisor export --format json
llm-advisor export --format markdown
```

## 📖 Detailed Guide

### How It Works

1. **Hardware Detection**: Scans your system using platform-specific tools (`nvidia-smi`, `rocm-smi`, `system_profiler`, `lspci`)
2. **VRAM Calculation**: Estimates VRAM requirements for each model at different quantization levels
3. **Fitness Scoring**: Scores each model based on how well it fits your hardware (VRAM utilization, quantization quality, context length support)
4. **Recommendation**: Sorts models by fitness score and provides ready-to-run commands

### Supported GPU Vendors

| Vendor | Detection Method | Status |
|--------|-----------------|--------|
| NVIDIA | nvidia-smi | ✅ Full Support |
| AMD | rocm-smi / lspci | ✅ Full Support |
| Apple Silicon | system_profiler | ✅ Full Support |
| Intel Arc | lspci / intel_gpu_top | ✅ Full Support |
| No GPU | CPU-only mode | ✅ Supported |

### Model Categories

- `general` — General-purpose chat and text generation
- `coding` — Code generation and programming assistance
- `math` — Mathematical reasoning
- `reasoning` — Logical reasoning and analysis
- `chat` — Conversational AI

### Quantization Explained

| Quantization | VRAM Usage | Quality | Speed |
|-------------|-----------|---------|-------|
| FP16 | 100% | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ |
| INT8 | ~50% | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ |
| INT4 | ~25% | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ |

## 💡 Design Philosophy & Roadmap

### Design Philosophy
- **Offline First**: Built-in model database, no network required for recommendations
- **Cross-Platform**: Works on Windows, macOS, and Linux
- **User Friendly**: Beautiful Rich terminal UI with tables, colors, and panels
- **Extensible**: Easy to add new models to the database

### Roadmap
- [ ] Online model database sync (fetch latest models from HuggingFace)
- [ ] GPU benchmark integration (actual performance testing)
- [ ] Docker support
- [ ] Web UI dashboard
- [ ] Plugin system for custom recommendation strategies

## 📦 Build & Deploy

### Build Executable

```bash
python build.py
```

This generates a standalone executable using PyInstaller.

### System Requirements

- Python 3.9+
- Windows / macOS / Linux
- No GPU required (CPU-only mode supported)

## 🤝 Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'feat: add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

Please read [CONTRIBUTING.md](CONTRIBUTING.md) for details on our code of conduct.

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- [Ollama](https://ollama.ai/) for making local LLMs accessible
- [llama.cpp](https://github.com/ggerganov/llama.cpp) for efficient LLM inference
- All open-source LLM providers (Meta, Qwen, DeepSeek, Mistral, etc.)

---

<div align="center">
  Made with ❤️ by <a href="https://github.com/gitstq">gitstq</a>
  <br/>
  <sub>⭐ Star this repo if you find it helpful!</sub>
</div>
