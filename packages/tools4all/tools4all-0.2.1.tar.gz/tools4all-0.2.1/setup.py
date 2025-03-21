#!/usr/bin/env python
"""
Setup script for Tools4All
"""
from setuptools import setup, find_packages

# Read the contents of README.md
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

# Read the requirements
with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = fh.read().splitlines()

setup(
    name="tools4all",
    version="0.2.1",
    author="Alfred Wallace",
    author_email="alfred.wallace@netcraft.fr",
    description="Function calling capabilities for LLMs that don't natively support them",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/alfredwallace7/tools4all",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    entry_points={
        "console_scripts": [
            "tools4all-cli=tools4all_cli:main",
            "tools4all-chat=tools4all_chat:main",
        ],
    },
)
