from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="ncos",
    version="21.7.2",
    author="ncOS Team",
    description="Neural Cognitive Operating System - Voice-Enabled Trading Platform",
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=find_packages(),
    python_requires=">=3.8",
    install_requires=[
        "pydantic>=1.8.0",
        "fastapi>=0.68.0",
        "uvicorn>=0.15.0",
        "streamlit>=1.0.0",
        "pandas>=1.3.0",
        "numpy>=1.21.0",
        "pyyaml>=5.4.0",
        "python-dotenv>=0.19.0",
        "aiofiles>=0.8.0",
        "websockets>=10.0",
        "sqlalchemy>=1.4.0",
        "redis>=4.0.0",
        "celery>=5.2.0",
        "pytest>=6.2.0",
        "pytest-asyncio>=0.18.0",
        "black>=21.0",
        "flake8>=4.0.0",
        "mypy>=0.910",
    ],
    entry_points={
        "console_scripts": [
            "ncos=core.main:main",
            "ncos-api=api.main:main",
            "ncos-voice=voice.ncos_voice_unified:main",
        ],
    },
)
