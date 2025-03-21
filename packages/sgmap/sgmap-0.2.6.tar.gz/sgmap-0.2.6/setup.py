#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import setup, find_packages

setup(
    name="sgmap",
    use_scm_version=True,
    description="AWS Security Group Mapping Tool",
    author="youyo",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    install_requires=[
        "boto3>=1.20.0",
        "click>=8.0.0",
    ],
    python_requires=">=3.12.0",
    entry_points={
        "console_scripts": [
            "sgmap=sgmap.cli:main",
        ],
    },
    setup_requires=["setuptools_scm>=6.2"],
)