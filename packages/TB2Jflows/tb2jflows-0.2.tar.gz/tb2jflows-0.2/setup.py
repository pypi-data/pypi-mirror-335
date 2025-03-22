#!/usr/bin/env python
from setuptools import find_packages, setup

__version__ = "0.2"

long_description = """ TB2Jflows: Workflows for automatically calculation of exchange parameters using TB2J """

setup(
    name="TB2Jflows",
    version=__version__,
    description="TB2Jflows: Workflows for automatically calculation of exchange parameters using TB2J",
    long_description=long_description,
    author="Xu He",
    author_email="mailhexu@gmail.com",
    license="BSD-2-clause",
    packages=find_packages(),
    scripts=[],
    install_requires=["TB2J", "ase", "sisl", "pyDFTutils"],
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
        "Intended Audience :: Science/Research",
        "Topic :: Scientific/Engineering :: Chemistry",
        "Topic :: Scientific/Engineering :: Physics",
        "License :: OSI Approved :: BSD License",
    ],
    python_requires=">=3.6",
)
