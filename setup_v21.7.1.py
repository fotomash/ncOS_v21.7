#!/usr/bin/env python3
"""
NCOS v21.7.1 Phoenix Mesh Setup Script
Neural Cognitive Operating System - Complete AI Trading Ecosystem
"""

from setuptools import setup, find_packages
import os

# Read README for long description
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

# Read requirements
with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

# Version information
VERSION = "21.7.1"
DESCRIPTION = "Neural Cognitive Operating System - Complete AI Trading Ecosystem"

setup(
    name="ncos-phoenix-mesh",
    version=VERSION,
    author="NCOS Team",
    author_email="team@ncos.ai",
    description=DESCRIPTION,
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/ncos/phoenix-mesh",
    project_urls={
        "Bug Tracker": "https://github.com/ncos/phoenix-mesh/issues",
        "Documentation": "https://docs.ncos.ai",
        "Source Code": "https://github.com/ncos/phoenix-mesh",
    },
    packages=find_packages(),
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Financial and Insurance Industry",
        "Intended Audience :: Developers",
        "Topic :: Office/Business :: Financial :: Investment",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.9",
    install_requires=requirements,
    extras_require={
        "dev": [
            "pytest>=7.4.0",
            "pytest-asyncio>=0.21.0",
            "pytest-cov>=4.1.0",
            "black>=23.0.0",
            "flake8>=6.0.0",
            "mypy>=1.4.0",
            "pre-commit>=3.3.0",
        ],
        "docs": [
            "mkdocs>=1.4.0",
            "mkdocs-material>=9.1.0",
            "mkdocs-mermaid2-plugin>=1.1.0",
        ],
        "gpu": [
            "torch>=2.0.0+cu118",
            "faiss-gpu>=1.7.4",
        ],
        "analytics": [
            "plotly>=5.15.0",
            "dash>=2.11.0",
            "streamlit>=1.24.0",
        ],
        "brokers": [
            "ib-insync>=0.9.86",
            "alpaca-trade-api>=3.0.0",
            "binance-connector>=3.2.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "ncos=ncos.cli:main",
            "ncos-launch=ncos.agents.master_orchestrator:main",
            "ncos-validate=ncos.utils.validation:main",
            "ncos-monitor=ncos.monitoring.dashboard:main",
        ],
    },
    include_package_data=True,
    package_data={
        "ncos": [
            "configs/*.yaml",
            "configs/*.json",
            "configs/*.toml",
            "configs/**/*.yaml",
            "configs/**/*.json",
            "templates/*.yaml",
            "templates/*.json",
            "schemas/*.json",
        ],
    },
    zip_safe=False,
    keywords=[
        "trading",
        "ai",
        "machine-learning",
        "algorithmic-trading",
        "smart-money-concepts",
        "wyckoff",
        "multi-agent-system",
        "neural-network",
        "financial-markets",
        "risk-management",
        "portfolio-management",
        "market-analysis",
        "technical-analysis",
        "quantitative-finance",
    ],
)
