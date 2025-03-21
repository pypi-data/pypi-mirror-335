#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="oect_excel_processor",
    version="0.1.0",
    author="OECT Research Team",
    author_email="your.email@example.com",
    description="处理OECT性能测试后的Excel数据并转换为CSV格式",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Durian-leader/oect-excel-processor",
    project_urls={
        "Bug Tracker": "https://github.com/Durian-leader/oect-excel-processor/issues",
        "Documentation": "https://github.com/Durian-leader/oect-excel-processor/wiki",
    },
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Science/Research",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Topic :: Scientific/Engineering",
    ],
    python_requires=">=3.6",
    install_requires=[
        "pandas>=1.0.0",
        "numpy>=1.18.0",
        "natsort>=7.0.0",
    ],
    extras_require={
        "dev": [
            "pytest>=6.0",
            "pytest-cov>=2.0",
            "black>=22.0",
            "isort>=5.0",
            "flake8>=3.9",
        ],
    },
    entry_points={
        "console_scripts": [
            "oect-processor=oect_excel_processor.cli:main",
        ],
    },
    include_package_data=True,
) 