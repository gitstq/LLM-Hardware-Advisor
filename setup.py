"""
Setup script for LLM Hardware Advisor.
"""

from setuptools import find_packages, setup

with open("README.md", "r", encoding="utf-8") as f:
    long_description = f.read()

with open("requirements.txt", "r", encoding="utf-8") as f:
    requirements = [line.strip() for line in f if line.strip() and not line.startswith("#")]

setup(
    name="llm-hardware-advisor",
    version="1.0.0",
    description="Detect your hardware and recommend the best local LLMs to run",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="LLM-Hardware-Advisor",
    author_email="",
    url="https://github.com/user/llm-hardware-advisor",
    license="MIT",
    packages=find_packages(),
    package_data={
        "llm_hardware_advisor.database": ["models.json"],
    },
    include_package_data=True,
    python_requires=">=3.8",
    install_requires=requirements,
    extras_require={
        "dev": [
            "pytest>=7.0",
            "pytest-cov>=4.0",
            "pyinstaller>=5.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "llm-advisor=llm_hardware_advisor.cli:main",
        ],
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Environment :: Console",
        "Intended Audience :: Developers",
        "Intended Audience :: End Users/Desktop",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Topic :: System :: Hardware",
        "Topic :: Utilities",
    ],
    keywords=[
        "llm",
        "hardware",
        "gpu",
        "recommendation",
        "local-ai",
        "ollama",
        "llama.cpp",
    ],
)
