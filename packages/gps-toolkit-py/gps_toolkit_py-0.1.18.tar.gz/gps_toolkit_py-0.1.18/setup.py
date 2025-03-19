#!/usr/bin/env python3

from setuptools import setup, find_packages

# This setup.py is a thin wrapper around the configuration in pyproject.toml
# We keep it for compatibility with older tools

setup(
    name="gps-toolkit-py",
    version="0.1.18",
    description="A Python package for working with GPS coordinates",
    author="GPS Tools Team",
    author_email="example@example.com",
    url="https://github.com/username/gps-toolkit-py",
    package_dir={"": "src"},
    packages=find_packages(where="src", exclude=["tests*", "examples*", "documentation*"]),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.7",
    install_requires=[
        "numpy",
        "scipy",
        "pyproj",
    ],
    extras_require={
        "dev": [
            "pytest>=6.0",
            "pytest-cov",
            "black",
            "flake8",
            "mypy",
            "pre-commit",
        ],
        "viz": [
            "matplotlib",
            "folium",
        ],
        "gis": [
            "shapely",
            "geopandas",
        ],
    },
) 