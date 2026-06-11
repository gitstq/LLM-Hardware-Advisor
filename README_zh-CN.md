<div align="center">
  <img src="assets/logo.png" alt="LLM Hardware Advisor Logo" width="120" height="120">

# 🤖 LLM-Hardware-Advisor

**检测你的硬件配置，找到最适合本地运行的大语言模型。**

[![Python 3.9+](https://img.shields.io/badge/python-3.9%2B-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Tests](https://img.shields.io/badge/tests-61%20passing-brightgreen.svg)]()
[![Models](https://img.shields.io/badge/models-66%2B-orange.svg)]()

**LLM-Hardware-Advisor** 是一款智能命令行工具，能够自动检测你的系统硬件（CPU、GPU、内存、磁盘），并推荐你可以在本地运行的最佳开源大语言模型——提供最优量化设置、上下文长度估算，以及开箱即用的 Ollama 和 llama.cpp 启动命令。

✨ **支持 NVIDIA、AMD、Apple Silicon 和 Intel Arc GPU。**

</div>

---

## ✨ 核心特性

| 特性 | 描述 |
|------|------|
| 🖥️ **硬件检测** | 自动检测 CPU、GPU（NVIDIA/AMD/Apple Silicon/Intel Arc）、内存、磁盘、操作系统 |
| 🧠 **66+ 模型数据库** | 内置数据库，涵盖 Llama、Qwen、DeepSeek、Mistral、Phi、Gemma、CodeLlama 等主流模型 |
| 📊 **智能评分** | 基于显存、量化和上下文长度的适配度评分（0-100） |
| 🔢 **多量化策略** | INT4 / INT8 / FP16 量化方案推荐 |
| 🌐 **双语支持** | 支持英文和中文（中文）界面 |
| 📤 **导出报告** | 支持导出为 JSON 或 Markdown 格式 |
| 🚀 **即用命令** | 自动生成 Ollama 和 llama.cpp 启动命令 |
| 🧪 **充分测试** | 61 个单元测试，覆盖全面 |

## 🚀 快速开始

### 安装

```bash
# 克隆仓库
git clone https://github.com/gitstq/LLM-Hardware-Advisor.git
cd LLM-Hardware-Advisor

# 安装依赖
pip install -r requirements.txt

# 或以包的形式安装
pip install .
```

### 使用方法

```bash
# 仅检测硬件
llm-advisor detect

# 获取 LLM 推荐结果（默认）
llm-advisor recommend

# 以中文输出推荐结果
llm-advisor recommend --lang zh

# 按类别筛选
llm-advisor recommend --category coding
llm-advisor recommend --category general
llm-advisor recommend --category math

# 对比两个模型
llm-advisor compare "Llama 3.1 8B" "Qwen 2.5 7B"

# 列出所有内置模型
llm-advisor list-models

# 导出报告
llm-advisor export --format json
llm-advisor export --format markdown
```

## 📖 详细使用指南

### 工作原理

1. **硬件检测**：使用平台特定工具（`nvidia-smi`、`rocm-smi`、`system_profiler`、`lspci`）扫描你的系统
2. **显存计算**：估算每个模型在不同量化级别下的显存需求
3. **适配度评分**：根据模型与硬件的匹配程度进行评分（显存利用率、量化质量、上下文长度支持）
4. **推荐输出**：按适配度评分排序，并提供可直接运行的启动命令

### 支持的 GPU 厂商

| 厂商 | 检测方式 | 状态 |
|------|---------|------|
| NVIDIA | nvidia-smi | ✅ 完全支持 |
| AMD | rocm-smi / lspci | ✅ 完全支持 |
| Apple Silicon | system_profiler | ✅ 完全支持 |
| Intel Arc | lspci / intel_gpu_top | ✅ 完全支持 |
| 无 GPU | 仅 CPU 模式 | ✅ 支持 |

### 模型分类

- `general` — 通用对话和文本生成
- `coding` — 代码生成和编程辅助
- `math` — 数学推理
- `reasoning` — 逻辑推理与分析
- `chat` — 对话式 AI

### 量化说明

| 量化方式 | 显存占用 | 质量 | 速度 |
|---------|---------|------|------|
| FP16 | 100% | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ |
| INT8 | ~50% | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ |
| INT4 | ~25% | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ |

## 💡 设计思路与迭代规划

### 设计思路
- **离线优先**：内置模型数据库，推荐过程无需联网
- **跨平台**：支持 Windows、macOS 和 Linux
- **用户友好**：精美的 Rich 终端 UI，包含表格、色彩和面板
- **易于扩展**：轻松添加新模型到数据库

### 迭代规划
- [ ] 在线模型数据库同步（从 HuggingFace 获取最新模型）
- [ ] GPU 基准测试集成（实际性能测试）
- [ ] Docker 支持
- [ ] Web UI 仪表盘
- [ ] 插件系统，支持自定义推荐策略

## 📦 打包与部署指南

### 构建可执行文件

```bash
python build.py
```

此命令将使用 PyInstaller 生成独立的可执行文件。

### 系统要求

- Python 3.9+
- Windows / macOS / Linux
- 无需 GPU（支持仅 CPU 模式）

## 🤝 贡献指南

欢迎贡献代码！请按照以下步骤操作：

1. Fork 本仓库
2. 创建功能分支（`git checkout -b feature/amazing-feature`）
3. 提交更改（`git commit -m 'feat: add amazing feature'`）
4. 推送到分支（`git push origin feature/amazing-feature`）
5. 发起 Pull Request

请阅读 [CONTRIBUTING.md](CONTRIBUTING.md) 了解我们的行为准则。

## 📄 开源协议说明

本项目基于 MIT 协议开源——详见 [LICENSE](LICENSE) 文件。

## 🙏 致谢

- [Ollama](https://ollama.ai/) 让本地运行大语言模型变得简单
- [llama.cpp](https://github.com/ggerganov/llama.cpp) 提供高效的 LLM 推理能力
- 所有开源大语言模型提供方（Meta、Qwen、DeepSeek、Mistral 等）

---

<div align="center">
  由 <a href="https://github.com/gitstq">gitstq</a> 用 ❤️ 制作
  <br/>
  <sub>⭐ 如果觉得有帮助，请给本仓库点个 Star！</sub>
</div>
