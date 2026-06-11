"""
Report formatting module.

Provides formatting for hardware detection results and model recommendations
in terminal table (Rich), JSON, and Markdown formats.
"""

import json
from typing import Any, Dict, List, Optional

from ..advisor.engine import HardwareProfile, Recommendation


class ReportFormatter:
    """Formats reports in multiple output formats."""

    def __init__(self, lang: str = "en") -> None:
        """
        Initialize the formatter.

        Args:
            lang: Language for output ("en" or "zh").
        """
        self.lang = lang

    def format_hardware_detection(
        self,
        hardware: HardwareProfile,
        fmt: str = "terminal",
    ) -> str:
        """
        Format hardware detection results.

        Args:
            hardware: Detected hardware profile.
            fmt: Output format ("terminal", "json", "markdown").

        Returns:
            Formatted string.
        """
        if fmt == "json":
            return self._hardware_to_json(hardware)
        elif fmt == "markdown":
            return self._hardware_to_markdown(hardware)
        else:
            return self._hardware_to_terminal(hardware)

    def format_recommendations(
        self,
        recommendations: List[Recommendation],
        hardware: HardwareProfile,
        fmt: str = "terminal",
    ) -> str:
        """
        Format model recommendations.

        Args:
            recommendations: List of recommendations.
            hardware: Hardware profile for context.
            fmt: Output format ("terminal", "json", "markdown").

        Returns:
            Formatted string.
        """
        if fmt == "json":
            return self._recommendations_to_json(recommendations, hardware)
        elif fmt == "markdown":
            return self._recommendations_to_markdown(recommendations, hardware)
        else:
            return self._recommendations_to_terminal(recommendations, hardware)

    def format_model_list(
        self,
        models: List[Any],
        fmt: str = "terminal",
    ) -> str:
        """
        Format a list of models.

        Args:
            models: List of ModelInfo objects.
            fmt: Output format ("terminal", "json", "markdown").

        Returns:
            Formatted string.
        """
        if fmt == "json":
            return self._model_list_to_json(models)
        elif fmt == "markdown":
            return self._model_list_to_markdown(models)
        else:
            return self._model_list_to_terminal(models)

    def format_comparison(
        self,
        comparison: Dict[str, Any],
        fmt: str = "terminal",
    ) -> str:
        """
        Format model comparison results.

        Args:
            comparison: Comparison dictionary from AdvisorEngine.
            fmt: Output format ("terminal", "json", "markdown").

        Returns:
            Formatted string.
        """
        if fmt == "json":
            return json.dumps(comparison, indent=2, ensure_ascii=False)
        elif fmt == "markdown":
            return self._comparison_to_markdown(comparison)
        else:
            return self._comparison_to_terminal(comparison)

    # ---- Terminal (Rich-compatible plain text) formatting ----

    def _hardware_to_terminal(self, hardware: HardwareProfile) -> str:
        """Format hardware info as a Rich-compatible terminal table."""
        lines: List[str] = []

        # CPU section
        lines.append(f"[bold cyan]{'CPU Information' if self.lang == 'en' else 'CPU 信息'}[/bold cyan]")
        cpu = hardware.cpu
        if cpu.get("model"):
            lines.append(f"  {'Model' if self.lang == 'en' else '型号'}: {cpu['model']}")
        if cpu.get("vendor"):
            lines.append(f"  {'Vendor' if self.lang == 'en' else '厂商'}: {cpu['vendor']}")
        if cpu.get("architecture"):
            lines.append(f"  {'Architecture' if self.lang == 'en' else '架构'}: {cpu['architecture']}")
        if cpu.get("physical_cores"):
            lines.append(f"  {'Physical Cores' if self.lang == 'en' else '物理核心'}: {cpu['physical_cores']}")
        if cpu.get("logical_cores"):
            lines.append(f"  {'Logical Cores' if self.lang == 'en' else '逻辑核心'}: {cpu['logical_cores']}")
        if cpu.get("frequency_mhz"):
            lines.append(f"  {'Frequency' if self.lang == 'en' else '频率'}: {cpu['frequency_mhz']} MHz")
        lines.append("")

        # GPU section
        lines.append(f"[bold cyan]{'GPU Information' if self.lang == 'en' else 'GPU 信息'}[/bold cyan]")
        if hardware.has_gpu:
            for i, gpu in enumerate(hardware.gpus):
                if len(hardware.gpus) > 1:
                    lines.append(f"  GPU #{i + 1}:")
                if gpu.get("vendor"):
                    lines.append(f"    {'Vendor' if self.lang == 'en' else '厂商'}: {gpu['vendor']}")
                if gpu.get("model"):
                    lines.append(f"    {'Model' if self.lang == 'en' else '型号'}: {gpu['model']}")
                if gpu.get("vram_total_gb"):
                    lines.append(f"    {'VRAM' if self.lang == 'en' else '显存'}: {gpu['vram_total_gb']} GB")
                if gpu.get("vram_free_gb"):
                    lines.append(f"    {'Free VRAM' if self.lang == 'en' else '可用显存'}: {gpu['vram_free_gb']} GB")
                if gpu.get("driver_version"):
                    lines.append(f"    {'Driver' if self.lang == 'en' else '驱动版本'}: {gpu['driver_version']}")
                if gpu.get("cuda_version"):
                    lines.append(f"    {'CUDA' if self.lang == 'en' else 'CUDA版本'}: {gpu['cuda_version']}")
        else:
            lines.append(
                f"  [yellow]{'No GPU detected. Models will run on CPU only.' if self.lang == 'en' else '未检测到GPU，模型将以CPU模式运行。'}[/yellow]"
            )
        lines.append("")

        # Memory section
        lines.append(f"[bold cyan]{'Memory' if self.lang == 'en' else '内存'}[/bold cyan]")
        mem = hardware.memory
        if mem.get("total_gb"):
            lines.append(f"  {'Total RAM' if self.lang == 'en' else '总内存'}: {mem['total_gb']} GB")
        if mem.get("available_gb"):
            lines.append(f"  {'Available' if self.lang == 'en' else '可用内存'}: {mem['available_gb']} GB")
        if mem.get("used_gb"):
            lines.append(f"  {'Used' if self.lang == 'en' else '已使用'}: {mem['used_gb']} GB")
        lines.append("")

        # System section
        lines.append(f"[bold cyan]{'System' if self.lang == 'en' else '系统'}[/bold cyan]")
        sys_info = hardware.system
        if sys_info.get("os_name"):
            lines.append(f"  {'OS' if self.lang == 'en' else '操作系统'}: {sys_info['os_name']}")
        if sys_info.get("os_version"):
            lines.append(f"  {'Version' if self.lang == 'en' else '版本'}: {sys_info['os_version']}")
        if sys_info.get("python_version"):
            lines.append(f"  {'Python' if self.lang == 'en' else 'Python版本'}: {sys_info['python_version']}")
        if sys_info.get("disk_free_gb"):
            lines.append(f"  {'Free Disk' if self.lang == 'en' else '可用磁盘'}: {sys_info['disk_free_gb']} GB")

        return "\n".join(lines)

    def _recommendations_to_terminal(
        self,
        recommendations: List[Recommendation],
        hardware: HardwareProfile,
    ) -> str:
        """Format recommendations as a Rich-compatible terminal table."""
        lines: List[str] = []

        if not recommendations:
            lines.append(
                f"[red]{'No models found that match your hardware.' if self.lang == 'en' else '未找到适合您硬件的模型。'}[/red]"
            )
            return "\n".join(lines)

        # Header
        header = "Model Recommendations" if self.lang == "en" else "模型推荐"
        lines.append(f"[bold green]{header}[/bold green]")
        lines.append("")

        # Hardware summary
        if hardware.has_gpu:
            lines.append(
                f"  {'Available VRAM' if self.lang == 'en' else '可用显存'}: "
                f"{hardware.max_single_gpu_vram_gb:.1f} GB | "
                f"{'RAM' if self.lang == 'en' else '内存'}: {hardware.total_ram_gb:.1f} GB"
            )
        else:
            lines.append(
                f"  {'RAM' if self.lang == 'en' else '内存'}: {hardware.total_ram_gb:.1f} GB (CPU mode)"
            )
        lines.append("")

        # Table header
        lines.append(
            f"  {'#':<4} {'Score':<8} {'Model':<35} {'Params':<12} {'Quant':<8} "
            f"{'VRAM':<8} {'Mode':<8} {'Category':<12}"
        )
        lines.append("  " + "-" * 100)

        for i, rec in enumerate(recommendations, 1):
            model = rec.model
            mode = "GPU" if rec.can_run_on_gpu else "CPU"
            score_color = "[green]" if rec.fitness_score >= 70 else "[yellow]" if rec.fitness_score >= 40 else "[red]"
            quant_display = rec.quant_level.upper()

            line = (
                f"  {i:<4} {score_color}{rec.fitness_score:<8.1f}[/] "
                f"{model.name:<35} {model.parameter_count:<12} "
                f"{quant_display:<8} {rec.estimated_vram_gb:<7.1f}GB "
                f"{mode:<8} {model.category:<12}"
            )
            lines.append(line)

        lines.append("")

        # Detailed recommendations for top 3
        detail_header = "Top Recommendations Details" if self.lang == "en" else "推荐详情（前三）"
        lines.append(f"[bold]{detail_header}[/bold]")
        lines.append("")

        for i, rec in enumerate(recommendations[:3], 1):
            model = rec.model
            lines.append(f"  [bold cyan]{i}. {model.name}[/bold cyan]")
            lines.append(f"     {'Provider' if self.lang == 'en' else '提供方'}: {model.provider}")
            lines.append(f"     {'Parameters' if self.lang == 'en' else '参数量'}: {model.parameter_count}")
            lines.append(f"     {'Context' if self.lang == 'en' else '上下文'}: {model.context_length:,} tokens")
            lines.append(f"     {'License' if self.lang == 'en' else '许可证'}: {model.license}")
            lines.append(f"     {'Quantization' if self.lang == 'en' else '量化'}: {rec.quant_level.upper()}")
            lines.append(f"     {'Est. VRAM' if self.lang == 'en' else '预估显存'}: {rec.estimated_vram_gb:.1f} GB")
            lines.append(f"     {'Run Mode' if self.lang == 'en' else '运行模式'}: {'GPU' if rec.can_run_on_gpu else 'CPU'}")
            lines.append(f"     HuggingFace: {model.huggingface_id}")
            lines.append(f"     {'Commands' if self.lang == 'en' else '运行命令'}:")
            for cmd_type, cmd in rec.run_commands.items():
                if cmd_type != "download":
                    lines.append(f"       [dim]{cmd_type}:[/] {cmd}")
            lines.append("")

        return "\n".join(lines)

    def _model_list_to_terminal(self, models: List[Any]) -> str:
        """Format a model list as a terminal table."""
        lines: List[str] = []
        lines.append(f"[bold green]{'All Models in Database' if self.lang == 'en' else '数据库中的所有模型'} ({len(models)})[/bold green]")
        lines.append("")
        lines.append(
            f"  {'Model':<40} {'Provider':<20} {'Params':<12} {'Context':<10} {'Category':<12} {'License':<25}"
        )
        lines.append("  " + "-" * 125)

        for model in models:
            lines.append(
                f"  {model.name:<40} {model.provider:<20} {model.parameter_count:<12} "
                f"{model.context_length:<10,} {model.category:<12} {model.license:<25}"
            )

        return "\n".join(lines)

    def _comparison_to_terminal(self, comparison: Dict[str, Any]) -> str:
        """Format comparison as terminal output."""
        lines: List[str] = []

        if "error" in comparison:
            lines.append(f"[red]{comparison['error']}[/red]")
            return "\n".join(lines)

        m1 = comparison.get("model1", {})
        m2 = comparison.get("model2", {})

        lines.append(f"[bold green]{'Model Comparison' if self.lang == 'en' else '模型对比'}[/bold green]")
        lines.append("")

        fields = [
            ("name", "Model" if self.lang == "en" else "模型"),
            ("provider", "Provider" if self.lang == "en" else "提供方"),
            ("parameter_count", "Parameters" if self.lang == "en" else "参数量"),
            ("context_length", "Context" if self.lang == "en" else "上下文长度"),
            ("category", "Category" if self.lang == "en" else "类别"),
            ("license", "License" if self.lang == "en" else "许可证"),
        ]

        for field, label in fields:
            v1 = str(m1.get(field, "N/A"))
            v2 = str(m2.get(field, "N/A"))
            lines.append(f"  [bold]{label}[/bold]")
            lines.append(f"    {m1.get('name', 'Model 1')}: {v1}")
            lines.append(f"    {m2.get('name', 'Model 2')}: {v2}")
            lines.append("")

        # VRAM comparison
        lines.append(f"  [bold]{'VRAM Requirements' if self.lang == 'en' else '显存需求'} (GB)[/bold]")
        for quant in ["int4", "int8", "fp16"]:
            v1 = m1.get("vram_estimates", {}).get(quant, "N/A")
            v2 = m2.get("vram_estimates", {}).get(quant, "N/A")
            v1_str = f"{v1:.1f}" if isinstance(v1, (int, float)) else str(v1)
            v2_str = f"{v2:.1f}" if isinstance(v2, (int, float)) else str(v2)
            lines.append(f"    {quant.upper()}: {v1_str} GB vs {v2_str} GB")

        # Fitness comparison
        if "fitness_score" in m1 and "fitness_score" in m2:
            lines.append("")
            lines.append(f"  [bold]{'Fitness Score' if self.lang == 'en' else '适配度评分'}[/bold]")
            lines.append(f"    {m1.get('name', 'Model 1')}: {m1.get('fitness_score', 'N/A')}")
            lines.append(f"    {m2.get('name', 'Model 2')}: {m2.get('fitness_score', 'N/A')}")

        return "\n".join(lines)

    # ---- JSON formatting ----

    def _hardware_to_json(self, hardware: HardwareProfile) -> str:
        """Convert hardware profile to JSON string."""
        data = {
            "cpu": hardware.cpu,
            "gpus": hardware.gpus,
            "memory": hardware.memory,
            "system": hardware.system,
            "summary": {
                "total_vram_gb": hardware.total_vram_gb,
                "max_single_gpu_vram_gb": hardware.max_single_gpu_vram_gb,
                "total_ram_gb": hardware.total_ram_gb,
                "has_gpu": hardware.has_gpu,
                "gpu_vendor": hardware.gpu_vendor,
                "gpu_count": hardware.gpu_count,
            },
        }
        return json.dumps(data, indent=2, ensure_ascii=False)

    def _recommendations_to_json(
        self,
        recommendations: List[Recommendation],
        hardware: HardwareProfile,
    ) -> str:
        """Convert recommendations to JSON string."""
        recs = []
        for rec in recommendations:
            recs.append({
                "model": {
                    "name": rec.model.name,
                    "provider": rec.model.provider,
                    "parameter_count": rec.model.parameter_count,
                    "context_length": rec.model.context_length,
                    "category": rec.model.category,
                    "license": rec.model.license,
                    "huggingface_id": rec.model.huggingface_id,
                    "tags": rec.model.tags,
                },
                "recommended_quantization": rec.quant_level,
                "estimated_vram_gb": rec.estimated_vram_gb,
                "fitness_score": rec.fitness_score,
                "can_run_on_gpu": rec.can_run_on_gpu,
                "can_run_on_cpu": rec.can_run_on_cpu,
                "run_commands": rec.run_commands,
            })
        data = {
            "hardware_summary": {
                "total_vram_gb": hardware.total_vram_gb,
                "max_single_gpu_vram_gb": hardware.max_single_gpu_vram_gb,
                "total_ram_gb": hardware.total_ram_gb,
                "has_gpu": hardware.has_gpu,
            },
            "recommendations": recs,
            "total_count": len(recommendations),
        }
        return json.dumps(data, indent=2, ensure_ascii=False)

    def _model_list_to_json(self, models: List[Any]) -> str:
        """Convert model list to JSON string."""
        data = []
        for model in models:
            data.append({
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
            })
        return json.dumps(data, indent=2, ensure_ascii=False)

    # ---- Markdown formatting ----

    def _hardware_to_markdown(self, hardware: HardwareProfile) -> str:
        """Convert hardware profile to Markdown."""
        lines: List[str] = []
        lines.append("# " + ("Hardware Detection Report" if self.lang == "en" else "硬件检测报告"))
        lines.append("")

        # CPU
        lines.append("## " + ("CPU" if self.lang == "en" else "CPU"))
        cpu = hardware.cpu
        lines.append(f"| {'Item' if self.lang == 'en' else '项目'} | {'Value' if self.lang == 'en' else '值'} |")
        lines.append("|---|---|")
        for key, label in [
            ("model", "Model" if self.lang == "en" else "型号"),
            ("vendor", "Vendor" if self.lang == "en" else "厂商"),
            ("architecture", "Architecture" if self.lang == "en" else "架构"),
            ("physical_cores", "Physical Cores" if self.lang == "en" else "物理核心"),
            ("logical_cores", "Logical Cores" if self.lang == "en" else "逻辑核心"),
            ("frequency_mhz", "Frequency (MHz)" if self.lang == "en" else "频率 (MHz)"),
        ]:
            val = cpu.get(key)
            if val:
                lines.append(f"| {label} | {val} |")
        lines.append("")

        # GPU
        lines.append("## " + ("GPU" if self.lang == "en" else "GPU"))
        if hardware.has_gpu:
            for i, gpu in enumerate(hardware.gpus):
                if len(hardware.gpus) > 1:
                    lines.append(f"### GPU #{i + 1}")
                lines.append(f"| {'Item' if self.lang == 'en' else '项目'} | {'Value' if self.lang == 'en' else '值'} |")
                lines.append("|---|---|")
                for key, label in [
                    ("vendor", "Vendor" if self.lang == "en" else "厂商"),
                    ("model", "Model" if self.lang == "en" else "型号"),
                    ("vram_total_gb", "VRAM (GB)" if self.lang == "en" else "显存 (GB)"),
                    ("vram_free_gb", "Free VRAM (GB)" if self.lang == "en" else "可用显存 (GB)"),
                    ("driver_version", "Driver" if self.lang == "en" else "驱动"),
                    ("cuda_version", "CUDA" if self.lang == "en" else "CUDA版本"),
                ]:
                    val = gpu.get(key)
                    if val:
                        lines.append(f"| {label} | {val} |")
                lines.append("")
        else:
            lines.append("> " + ("No GPU detected." if self.lang == "en" else "未检测到GPU。"))
            lines.append("")

        # Memory
        lines.append("## " + ("Memory" if self.lang == "en" else "内存"))
        mem = hardware.memory
        lines.append(f"| {'Item' if self.lang == 'en' else '项目'} | {'Value' if self.lang == 'en' else '值'} |")
        lines.append("|---|---|")
        for key, label in [
            ("total_gb", "Total RAM (GB)" if self.lang == "en" else "总内存 (GB)"),
            ("available_gb", "Available (GB)" if self.lang == "en" else "可用 (GB)"),
            ("used_gb", "Used (GB)" if self.lang == "en" else "已使用 (GB)"),
        ]:
            val = mem.get(key)
            if val:
                lines.append(f"| {label} | {val} |")
        lines.append("")

        # System
        lines.append("## " + ("System" if self.lang == "en" else "系统"))
        sys_info = hardware.system
        lines.append(f"| {'Item' if self.lang == 'en' else '项目'} | {'Value' if self.lang == 'en' else '值'} |")
        lines.append("|---|---|")
        for key, label in [
            ("os_name", "OS" if self.lang == "en" else "操作系统"),
            ("os_version", "Version" if self.lang == "en" else "版本"),
            ("python_version", "Python" if self.lang == "en" else "Python版本"),
            ("disk_free_gb", "Free Disk (GB)" if self.lang == "en" else "可用磁盘 (GB)"),
        ]:
            val = sys_info.get(key)
            if val:
                lines.append(f"| {label} | {val} |")

        return "\n".join(lines)

    def _recommendations_to_markdown(
        self,
        recommendations: List[Recommendation],
        hardware: HardwareProfile,
    ) -> str:
        """Convert recommendations to Markdown."""
        lines: List[str] = []
        lines.append("# " + ("LLM Recommendations" if self.lang == "en" else "大模型推荐"))
        lines.append("")

        # Hardware summary
        lines.append("## " + ("Hardware Summary" if self.lang == "en" else "硬件概要"))
        if hardware.has_gpu:
            lines.append(
                f"- **{'GPU VRAM' if self.lang == 'en' else 'GPU显存'}**: {hardware.max_single_gpu_vram_gb:.1f} GB"
            )
        lines.append(f"- **{'RAM' if self.lang == 'en' else '内存'}**: {hardware.total_ram_gb:.1f} GB")
        lines.append("")

        # Recommendations table
        lines.append("## " + ("Recommended Models" if self.lang == "en" else "推荐模型"))
        lines.append("")
        lines.append(
            f"| # | {'Score' if self.lang == 'en' else '评分'} | "
            f"{'Model' if self.lang == 'en' else '模型'} | "
            f"{'Params' if self.lang == 'en' else '参数量'} | "
            f"{'Quant' if self.lang == 'en' else '量化'} | "
            f"{'VRAM' if self.lang == 'en' else '显存'} | "
            f"{'Mode' if self.lang == 'en' else '模式'} | "
            f"{'Category' if self.lang == 'en' else '类别'} |"
        )
        lines.append("|---|---|---|---|---|---|---|---|")

        for i, rec in enumerate(recommendations, 1):
            mode = "GPU" if rec.can_run_on_gpu else "CPU"
            lines.append(
                f"| {i} | {rec.fitness_score:.1f} | "
                f"{rec.model.name} | "
                f"{rec.model.parameter_count} | "
                f"{rec.quant_level.upper()} | "
                f"{rec.estimated_vram_gb:.1f} GB | "
                f"{mode} | "
                f"{rec.model.category} |"
            )

        lines.append("")

        # Detailed recommendations
        lines.append("## " + ("Details" if self.lang == "en" else "详情"))
        lines.append("")

        for i, rec in enumerate(recommendations[:5], 1):
            model = rec.model
            lines.append(f"### {i}. {model.name}")
            lines.append(f"- **{'Provider' if self.lang == 'en' else '提供方'}**: {model.provider}")
            lines.append(f"- **{'Parameters' if self.lang == 'en' else '参数量'}**: {model.parameter_count}")
            lines.append(f"- **{'Context' if self.lang == 'en' else '上下文'}**: {model.context_length:,} tokens")
            lines.append(f"- **{'License' if self.lang == 'en' else '许可证'}**: {model.license}")
            lines.append(f"- **{'Quantization' if self.lang == 'en' else '量化'}**: {rec.quant_level.upper()}")
            lines.append(f"- **{'Est. VRAM' if self.lang == 'en' else '预估显存'}**: {rec.estimated_vram_gb:.1f} GB")
            lines.append(f"- **{'Mode' if self.lang == 'en' else '模式'}**: {'GPU' if rec.can_run_on_gpu else 'CPU'}")
            lines.append(f"- **HuggingFace**: [{model.huggingface_id}](https://huggingface.co/{model.huggingface_id})")
            lines.append("")
            lines.append("**" + ("Run Commands" if self.lang == "en" else "运行命令") + "**:")
            for cmd_type, cmd in rec.run_commands.items():
                if cmd_type != "download":
                    lines.append(f"- `{cmd}`")
            lines.append("")

        return "\n".join(lines)

    def _model_list_to_markdown(self, models: List[Any]) -> str:
        """Convert model list to Markdown."""
        lines: List[str] = []
        lines.append(
            f"# {'All Models' if self.lang == 'en' else '所有模型'} ({len(models)})"
        )
        lines.append("")
        lines.append(
            f"| {'Model' if self.lang == 'en' else '模型'} | "
            f"{'Provider' if self.lang == 'en' else '提供方'} | "
            f"{'Params' if self.lang == 'en' else '参数量'} | "
            f"{'Context' if self.lang == 'en' else '上下文'} | "
            f"{'Category' if self.lang == 'en' else '类别'} | "
            f"{'License' if self.lang == 'en' else '许可证'} |"
        )
        lines.append("|---|---|---|---|---|---|")

        for model in models:
            lines.append(
                f"| {model.name} | "
                f"{model.provider} | "
                f"{model.parameter_count} | "
                f"{model.context_length:,} | "
                f"{model.category} | "
                f"{model.license} |"
            )

        return "\n".join(lines)

    def _comparison_to_markdown(self, comparison: Dict[str, Any]) -> str:
        """Convert comparison to Markdown."""
        lines: List[str] = []

        if "error" in comparison:
            lines.append(f"**Error**: {comparison['error']}")
            return "\n".join(lines)

        m1 = comparison.get("model1", {})
        m2 = comparison.get("model2", {})

        lines.append("# " + ("Model Comparison" if self.lang == "en" else "模型对比"))
        lines.append("")

        fields = [
            ("name", "Model" if self.lang == "en" else "模型"),
            ("provider", "Provider" if self.lang == "en" else "提供方"),
            ("parameter_count", "Parameters" if self.lang == "en" else "参数量"),
            ("context_length", "Context" if self.lang == "en" else "上下文长度"),
            ("category", "Category" if self.lang == "en" else "类别"),
            ("license", "License" if self.lang == "en" else "许可证"),
        ]

        lines.append(
            f"| {'Attribute' if self.lang == 'en' else '属性'} | "
            f"{m1.get('name', 'Model 1')} | "
            f"{m2.get('name', 'Model 2')} |"
        )
        lines.append("|---|---|---|")

        for field, label in fields:
            v1 = str(m1.get(field, "N/A"))
            v2 = str(m2.get(field, "N/A"))
            lines.append(f"| {label} | {v1} | {v2} |")

        lines.append("")
        lines.append("## " + ("VRAM Requirements (GB)" if self.lang == "en" else "显存需求 (GB)"))
        lines.append(
            f"| {'Quantization' if self.lang == 'en' else '量化'} | "
            f"{m1.get('name', 'Model 1')} | "
            f"{m2.get('name', 'Model 2')} |"
        )
        lines.append("|---|---|---|")

        for quant in ["int4", "int8", "fp16"]:
            v1 = m1.get("vram_estimates", {}).get(quant, "N/A")
            v2 = m2.get("vram_estimates", {}).get(quant, "N/A")
            v1_str = f"{v1:.1f}" if isinstance(v1, (int, float)) else str(v1)
            v2_str = f"{v2:.1f}" if isinstance(v2, (int, float)) else str(v2)
            lines.append(f"| {quant.upper()} | {v1_str} GB | {v2_str} GB |")

        return "\n".join(lines)
