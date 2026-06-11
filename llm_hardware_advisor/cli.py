"""
CLI entry point for LLM Hardware Advisor.

Uses Click for command-line interface and Rich for beautiful terminal output.
"""

import sys
from typing import Optional

try:
    import click
    from rich.console import Console
    from rich.panel import Panel
    from rich.progress import Progress, SpinnerColumn, TextColumn
    from rich.table import Table
    from rich.text import Text

    HAS_RICH = True
except ImportError:
    HAS_RICH = False

from .advisor.engine import AdvisorEngine, HardwareProfile
from .detector.cpu import detect_cpu
from .detector.gpu import detect_gpus
from .detector.memory import detect_memory
from .detector.system import detect_system
from .reporter.formatter import ReportFormatter
from .utils.constants import CATEGORIES, CATEGORY_NAMES, CATEGORY_NAMES_ZH

__version__ = "1.0.0"

# Create console instance
console = Console() if HAS_RICH else None


def _print(text: str) -> None:
    """Print text using Rich console or fallback to stdout."""
    if console:
        console.print(Text.from_markup(text))
    else:
        # Strip Rich markup tags for plain output
        import re
        clean = re.sub(r"\[/?[a-z_=\s]+\]", "", text)
        print(clean)


def _print_panel(title: str, content: str) -> None:
    """Print a Rich panel or plain text fallback."""
    if console:
        console.print(Panel(content, title=title, border_style="cyan"))
    else:
        print(f"\n{'=' * 60}")
        print(f" {title}")
        print(f"{'=' * 60}")
        print(content)
        print(f"{'=' * 60}\n")


def detect_hardware() -> HardwareProfile:
    """
    Run all hardware detection and return a HardwareProfile.

    Uses Rich progress indicators during detection.
    """
    cpu_info = {}
    gpu_info = []
    memory_info = {}
    system_info = {}

    if console:
        with Progress(
            SpinnerColumn(),
            TextColumn("[bold blue]{task.description}"),
            console=console,
            transient=True,
        ) as progress:
            task_cpu = progress.add_task("Detecting CPU...", total=None)
            cpu_info = detect_cpu()
            progress.update(task_cpu, completed=True)

            task_gpu = progress.add_task("Detecting GPU...", total=None)
            gpu_info = detect_gpus()
            progress.update(task_gpu, completed=True)

            task_mem = progress.add_task("Detecting memory...", total=None)
            memory_info = detect_memory()
            progress.update(task_mem, completed=True)

            task_sys = progress.add_task("Detecting system info...", total=None)
            system_info = detect_system()
            progress.update(task_sys, completed=True)
    else:
        cpu_info = detect_cpu()
        gpu_info = detect_gpus()
        memory_info = detect_memory()
        system_info = detect_system()

    return HardwareProfile(
        cpu=cpu_info,
        gpus=gpu_info,
        memory=memory_info,
        system=system_info,
    )


@click.group()
@click.version_option(version=__version__, prog_name="llm-advisor")
def main() -> None:
    """LLM Hardware Advisor - Detect hardware and recommend local LLMs."""
    pass


@main.command()
def detect() -> None:
    """Detect and display hardware configuration."""
    hardware = detect_hardware()
    formatter = ReportFormatter(lang="en")
    output = formatter.format_hardware_detection(hardware, fmt="terminal")
    _print_panel("Hardware Detection", output)


@main.command()
@click.option(
    "--category", "-c",
    type=click.Choice(CATEGORIES, case_sensitive=False),
    default=None,
    help="Filter recommendations by category.",
)
@click.option(
    "--lang", "-l",
    type=click.Choice(["en", "zh"], case_sensitive=False),
    default="en",
    help="Output language (en/zh).",
)
@click.option(
    "--top", "-n",
    type=int,
    default=10,
    help="Number of recommendations to show.",
)
@click.option(
    "--format", "-f",
    "fmt",
    type=click.Choice(["terminal", "json", "markdown"], case_sensitive=False),
    default="terminal",
    help="Output format.",
)
def recommend(
    category: Optional[str],
    lang: str,
    top: int,
    fmt: str,
) -> None:
    """Detect hardware and recommend suitable LLM models."""
    # Detect hardware
    hardware = detect_hardware()

    # Initialize engine and formatter
    engine = AdvisorEngine()
    formatter = ReportFormatter(lang=lang)

    # Get recommendations
    recommendations = engine.recommend(hardware, category=category, top_n=top)

    # Format and output
    output = formatter.format_recommendations(recommendations, hardware, fmt=fmt)

    if fmt == "terminal":
        # Show hardware detection first
        hw_output = formatter.format_hardware_detection(hardware, fmt="terminal")
        _print_panel("Hardware Detection", hw_output)
        print()
        _print_panel("Model Recommendations", output)
    else:
        print(output)


@main.command()
@click.option(
    "--category", "-c",
    type=click.Choice(CATEGORIES, case_sensitive=False),
    default=None,
    help="Filter models by category.",
)
@click.option(
    "--format", "-f",
    "fmt",
    type=click.Choice(["terminal", "json", "markdown"], case_sensitive=False),
    default="terminal",
    help="Output format.",
)
@click.option(
    "--lang", "-l",
    type=click.Choice(["en", "zh"], case_sensitive=False),
    default="en",
    help="Output language (en/zh).",
)
def list_models(
    category: Optional[str],
    fmt: str,
    lang: str,
) -> None:
    """List all models in the built-in database."""
    engine = AdvisorEngine()
    formatter = ReportFormatter(lang=lang)

    if category:
        models = engine.get_models_by_category(category)
    else:
        models = engine.get_all_models()

    output = formatter.format_model_list(models, fmt=fmt)

    if fmt == "terminal":
        _print_panel(
            f"Model Database ({len(models)} models)",
            output,
        )
    else:
        print(output)


@main.command("compare")
@click.argument("model1", type=str)
@click.argument("model2", type=str)
@click.option(
    "--format", "-f",
    "fmt",
    type=click.Choice(["terminal", "json", "markdown"], case_sensitive=False),
    default="terminal",
    help="Output format.",
)
@click.option(
    "--lang", "-l",
    type=click.Choice(["en", "zh"], case_sensitive=False),
    default="en",
    help="Output language (en/zh).",
)
def compare_models(
    model1: str,
    model2: str,
    fmt: str,
    lang: str,
) -> None:
    """Compare two models side by side."""
    engine = AdvisorEngine()
    formatter = ReportFormatter(lang=lang)

    # Optionally detect hardware for fitness comparison
    try:
        hardware = detect_hardware()
    except Exception:
        hardware = None

    comparison = engine.compare_models(model1, model2, hardware=hardware)
    output = formatter.format_comparison(comparison, fmt=fmt)

    if fmt == "terminal":
        _print_panel("Model Comparison", output)
    else:
        print(output)


@main.command()
@click.option(
    "--format", "-f",
    "fmt",
    type=click.Choice(["json", "markdown"], case_sensitive=False),
    default="json",
    help="Export format.",
)
@click.option(
    "--lang", "-l",
    type=click.Choice(["en", "zh"], case_sensitive=False),
    default="en",
    help="Output language (en/zh).",
)
@click.option(
    "--category", "-c",
    type=click.Choice(CATEGORIES, case_sensitive=False),
    default=None,
    help="Filter by category.",
)
@click.option(
    "--output", "-o",
    type=click.Path(),
    default=None,
    help="Output file path. Prints to stdout if not specified.",
)
def export(
    fmt: str,
    lang: str,
    category: Optional[str],
    output: Optional[str],
) -> None:
    """Export hardware detection and recommendations to a file."""
    # Detect hardware
    hardware = detect_hardware()

    # Get recommendations
    engine = AdvisorEngine()
    recommendations = engine.recommend(hardware, category=category, top_n=20)

    # Format
    formatter = ReportFormatter(lang=lang)

    if fmt == "json":
        # Combine hardware and recommendations into one JSON
        import json
        hw_data = json.loads(formatter.format_hardware_detection(hardware, fmt="json"))
        rec_data = json.loads(formatter.format_recommendations(recommendations, hardware, fmt="json"))
        combined = {
            "hardware": hw_data,
            "recommendations": rec_data,
        }
        content = json.dumps(combined, indent=2, ensure_ascii=False)
    else:
        hw_md = formatter.format_hardware_detection(hardware, fmt="markdown")
        rec_md = formatter.format_recommendations(recommendations, hardware, fmt="markdown")
        content = hw_md + "\n\n---\n\n" + rec_md

    # Output
    if output:
        with open(output, "w", encoding="utf-8") as f:
            f.write(content)
        _print(f"[green]{'Report exported to' if lang == 'en' else '报告已导出到'}: {output}[/green]")
    else:
        print(content)


if __name__ == "__main__":
    main()
