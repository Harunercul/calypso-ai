"""
Setup script for TÜBİTAK İP-2 AI Bot System
"""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as f:
    long_description = f.read()

setup(
    name="calypso-ai-bot",
    version="0.1.0",
    author="Harun Erçul",
    author_email="harun@mbgames.com",
    description="TÜBİTAK İP-2 AI Bot System for CALYPSO Game",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Harunercul/calypso-ai",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: Other/Proprietary License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Games/Entertainment",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
    ],
    python_requires=">=3.10",
    install_requires=[
        "torch>=2.0.0",
        "stable-baselines3>=2.0.0",
        "gymnasium>=0.29.0",
        "numpy>=1.24.0",
        "grpcio>=1.50.0",
        "grpcio-tools>=1.50.0",
        "protobuf>=4.21.0",
        "tensorboard>=2.14.0",
        "pyyaml>=6.0",
        "tqdm>=4.65.0",
        "rich>=13.0.0",
        "typer>=0.9.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-cov>=4.0.0",
            "black>=23.0.0",
            "isort>=5.12.0",
            "flake8>=6.0.0",
            "mypy>=1.0.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "calypso-train=scripts.train_agent:main",
            "calypso-server=scripts.start_server:main",
            "calypso-eval=scripts.evaluate:main",
        ],
    },
)
