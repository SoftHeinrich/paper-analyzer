#!/usr/bin/env python3
"""
Setup script for PaperHelper.
"""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="paperhelper",
    version="1.0.0",
    author="Paper Helper Team",
    author_email="paperhelper@example.com",
    description="A tool for scraping paper information from top conferences in SE, AI/ML, and NLP",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/paperhelper/paperhelper",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Scientific/Engineering :: Information Analysis",
        "Topic :: Internet :: WWW/HTTP :: Indexing/Search",
        "Topic :: Text Processing :: Markup :: HTML",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "black>=22.0.0",
            "flake8>=5.0.0",
            "mypy>=0.991",
        ],
        "advanced": [
            "selenium>=4.5.0",
            "scrapy>=2.6.0",
            "nltk>=3.7",
            "spacy>=3.4.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "paperhelper=main:main",
        ],
    },
    include_package_data=True,
    zip_safe=False,
)