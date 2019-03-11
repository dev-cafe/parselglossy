#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""The setup script."""

from setuptools import find_packages, setup

with open('README.rst') as readme_file:
    readme = readme_file.read()

with open('HISTORY.rst') as history_file:
    history = history_file.read()

requirements = [
    'Click>=6.0',
    'pyparsing>=2.2',
    'pyyaml>=3.13',
]

setup_requirements = []

test_requirements = []

setup(
    author="Roberto Di Remigio",
    author_email='roberto.diremigio@gmail.com',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
    ],
    description="Generic input parsing library, speaking in tongues",
    entry_points={
        'console_scripts': [
            'parselglossy=parselglossy.cli:cli',
        ],
    },
    install_requires=requirements,
    license="MIT license",
    long_description=readme + '\n\n' + history,
    include_package_data=True,
    keywords='parselglossy',
    name='parselglossy',
    packages=find_packages(include=['parselglossy']),
    setup_requires=setup_requirements,
    test_suite='tests',
    tests_require=test_requirements,
    url='https://github.com/dev-cafe/parselglossy',
    version='0.2.0',
    zip_safe=False,
)
