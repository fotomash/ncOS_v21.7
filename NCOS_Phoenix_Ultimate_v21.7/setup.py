from setuptools import setup, find_packages

setup(
    name="ncos-phoenix-session",
    version="21.7",
    author="NCOS Team",
    description="Advanced trading system with Smart Money Concepts",
    packages=find_packages(),
    install_requires=[
        "fastapi>=0.104.1",
        "uvicorn>=0.24.0",
        "numpy>=1.24.3",
        "pandas>=2.0.3",
    ],
    python_requires='>=3.9',
    entry_points={
        'console_scripts': [
            'ncos-phoenix=api.ncos_zbar_api:main',
        ],
    },
)
