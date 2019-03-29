#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""The setup script."""

from setuptools import find_packages, setup
from pathlib import Path

with open("README.rst") as readme_file:
    readme = readme_file.read()

with open("HISTORY.rst") as history_file:
    history = history_file.read()

# extract fields such as __version__ from __init__.py
_init_fields = {}
with Path("parselglossy/__init__.py").open("r") as f:
    exec(f.read(), _init_fields)

# fmt: off
requirements = [
    "click>=6.0",
    "pyparsing>=2.2",
    "pyyaml>=3.13",
]
# fmt: on

setup_requirements = []

test_requirements = []

setup(
    author=_init_fields["__author__"],
    author_email=_init_fields["__email__"],
    classifiers=[
        "Development Status :: 2 - Pre-Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Natural Language :: English",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Operating System :: OS Independent",
    ],
    description="Generic input parsing library, speaking in tongues",
    entry_points={"console_scripts": ["parselglossy=parselglossy.cli:cli"]},
    install_requires=requirements,
    license="MIT license",
    long_description=readme + "\n\n" + history,
    include_package_data=True,
    keywords="parselglossy",
    name="parselglossy",
    packages=find_packages(exclude=["tests", "docs"]),
    setup_requires=setup_requirements,
    test_suite="tests",
    tests_require=test_requirements,
    url="https://github.com/dev-cafe/parselglossy",
    version=_init_fields["__version__"],
    zip_safe=False,
)
