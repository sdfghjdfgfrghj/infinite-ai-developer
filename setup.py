#!/usr/bin/env python3
"""
Setup script for Infinite AI Developer
"""

from setuptools import setup, find_packages
import os

# Read README for long description
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

# Read requirements
with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="infinite-ai-developer",
    version="1.0.0",
    author="Infinite AI Developer Contributors",
    author_email="contributors@infinite-ai-developer.com",
    description="♾️ The world's first truly autonomous AI software development system with unlimited iterations",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/sdfghjdfgfrghj/infinite-ai-developer",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Software Development :: Code Generators",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
    ],
    python_requires=">=3.11",
    install_requires=requirements,
    entry_points={
        "console_scripts": [
            "infinite-ai=main_infinite:main",
        ],
    },
    include_package_data=True,
    package_data={
        "orchestrator": ["*.yaml"],
    },
)