"""
Setup script for NATS IPC SDK
"""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="nats-ipc-sdk",
    version="1.0.0",
    author="Ryan",
    description="Ultra-lightweight Inter-Process Communication SDK for NATS",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/ryan/nats-ipc-sdk",
    packages=find_packages(exclude=["tests*", "examples*", "benchmarks*"]),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.13",
    install_requires=[
        "nats-py>=2.6.0",
    ],
    extras_require={
        "dev": ["pytest", "pytest-asyncio", "pytest-cov"],
        "benchmarks": ["numpy"],
    },
)