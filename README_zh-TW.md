<div align="center">
  <img src="assets/logo.png" alt="LLM Hardware Advisor Logo" width="120" height="120">

# 🤖 LLM-Hardware-Advisor

**偵測你的硬體配置，找到最適合本地執行的大語言模型。**

[![Python 3.9+](https://img.shields.io/badge/python-3.9%2B-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Tests](https://img.shields.io/badge/tests-61%20passing-brightgreen.svg)]()
[![Models](https://img.shields.io/badge/models-66%2B-orange.svg)]()

**LLM-Hardware-Advisor** 是一款智慧命令列工具，能夠自動偵測你的系統硬體（CPU、GPU、記憶體、磁碟），並推薦你可以在本地執行的最佳開源大語言模型——提供最優量化設定、上下文長度估算，以及開箱即用的 Ollama 和 llama.cpp 啟動命令。

✨ **支援 NVIDIA、AMD、Apple Silicon 和 Intel Arc GPU。**

</div>

---

## ✨ 核心特性

| 特性 | 描述 |
|------|------|
| 🖥️ **硬體偵測** | 自動偵測 CPU、GPU（NVIDIA/AMD/Apple Silicon/Intel Arc）、記憶體、磁碟、作業系統 |
| 🧠 **66+ 模型資料庫** | 內建資料庫，涵蓋 Llama、Qwen、DeepSeek、Mistral、Phi、Gemma、CodeLlama 等主流模型 |
| 📊 **智慧評分** | 基於顯存、量化和上下文長度的適配度評分（0-100） |
| 🔢 **多量化策略** | INT4 / INT8 / FP16 量化方案推薦 |
| 🌐 **雙語支援** | 支援英文和中文（中文）介面 |
| 📤 **匯出報告** | 支援匯出為 JSON 或 Markdown 格式 |
| 🚀 **即用命令** | 自動生成 Ollama 和 llama.cpp 啟動命令 |
| 🧪 **充分測試** | 61 個單元測試，覆蓋全面 |

## 🚀 快速開始

### 安裝

```bash
# 克隆倉庫
git clone https://github.com/gitstq/LLM-Hardware-Advisor.git
cd LLM-Hardware-Advisor

# 安裝依賴
pip install -r requirements.txt

# 或以套件的形式安裝
pip install .
```

### 使用方法

```bash
# 僅偵測硬體
llm-advisor detect

# 取得 LLM 推薦結果（預設）
llm-advisor recommend

# 以中文輸出推薦結果
llm-advisor recommend --lang zh

# 依類別篩選
llm-advisor recommend --category coding
llm-advisor recommend --category general
llm-advisor recommend --category math

# 比較兩個模型
llm-advisor compare "Llama 3.1 8B" "Qwen 2.5 7B"

# 列出所有內建模型
llm-advisor list-models

# 匯出報告
llm-advisor export --format json
llm-advisor export --format markdown
```

## 📖 詳細使用指南

### 運作原理

1. **硬體偵測**：使用平台特定工具（`nvidia-smi`、`rocm-smi`、`system_profiler`、`lspci`）掃描你的系統
2. **顯存計算**：估算每個模型在不同量化級別下的顯存需求
3. **適配度評分**：根據模型與硬體的匹配程度進行評分（顯存利用率、量化品質、上下文長度支援）
4. **推薦輸出**：按適配度評分排序，並提供可直接執行的啟動命令

### 支援的 GPU 廠商

| 廠商 | 偵測方式 | 狀態 |
|------|---------|------|
| NVIDIA | nvidia-smi | ✅ 完全支援 |
| AMD | rocm-smi / lspci | ✅ 完全支援 |
| Apple Silicon | system_profiler | ✅ 完全支援 |
| Intel Arc | lspci / intel_gpu_top | ✅ 完全支援 |
| 無 GPU | 僅 CPU 模式 | ✅ 支援 |

### 模型分類

- `general` — 通用對話和文字生成
- `coding` — 程式碼生成和程式設計輔助
- `math` — 數學推理
- `reasoning` — 邏輯推理與分析
- `chat` — 對話式 AI

### 量化說明

| 量化方式 | 顯存佔用 | 品質 | 速度 |
|---------|---------|------|------|
| FP16 | 100% | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ |
| INT8 | ~50% | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ |
| INT4 | ~25% | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ |

## 💡 設計思路與迭代規劃

### 設計思路
- **離線優先**：內建模型資料庫，推薦過程無需連網
- **跨平台**：支援 Windows、macOS 和 Linux
- **使用者友善**：精美的 Rich 終端 UI，包含表格、色彩和面板
- **易於擴充**：輕鬆新增模型到資料庫

### 迭代規劃
- [ ] 線上模型資料庫同步（從 HuggingFace 取得最新模型）
- [ ] GPU 基準測試整合（實際效能測試）
- [ ] Docker 支援
- [ ] Web UI 儀表板
- [ ] 外掛系統，支援自訂推薦策略

## 📦 打包與部署指南

### 建構可執行檔

```bash
python build.py
```

此命令將使用 PyInstaller 生成獨立的可執行檔。

### 系統需求

- Python 3.9+
- Windows / macOS / Linux
- 無需 GPU（支援僅 CPU 模式）

## 🤝 貢獻指南

歡迎貢獻程式碼！請依照以下步驟操作：

1. Fork 本倉庫
2. 建立功能分支（`git checkout -b feature/amazing-feature`）
3. 提交變更（`git commit -m 'feat: add amazing feature'`）
4. 推送到分支（`git push origin feature/amazing-feature`）
5. 發起 Pull Request

請閱讀 [CONTRIBUTING.md](CONTRIBUTING.md) 了解我們的行為準則。

## 📄 開源協議說明

本專案基於 MIT 協議開源——詳見 [LICENSE](LICENSE) 檔案。

## 🙏 致謝

- [Ollama](https://ollama.ai/) 讓本地執行大語言模型變得簡單
- [llama.cpp](https://github.com/ggerganov/llama.cpp) 提供高效的 LLM 推理能力
- 所有開源大語言模型提供方（Meta、Qwen、DeepSeek、Mistral 等）

---

<div align="center">
  由 <a href="https://github.com/gitstq">gitstq</a> 用 ❤️ 製作
  <br/>
  <sub>⭐ 如果覺得有幫助，請給本倉庫點個 Star！</sub>
</div>
