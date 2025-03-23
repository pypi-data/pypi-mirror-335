#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import setup, find_packages

# Package metadata
__version__ = "0.1.0"

setup(
    name="recalldb",
    version=__version__,
    packages=find_packages(),
    description="Multi-user vector database with independent document access for each user",
    author="RecallDB Team",
    author_email="your.email@example.com",
    url="https://github.com/yourusername/recalldb",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Database",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
    ],
    python_requires=">=3.8",
    install_requires=[
        "numpy>=1.20.0",
        "pandas>=1.3.0",
        "pyarrow>=6.0.0",
        "scikit-learn>=1.0.0",
    ],
    extras_require={
        "dev": [
            "pytest>=6.0.0",
            "black>=22.0.0",
            "isort>=5.0.0",
            "mypy>=0.900",
        ],
    },
    keywords="vector database, embeddings, similarity search, multi-user",
) 