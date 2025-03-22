#!/usr/bin/env python3
from setuptools import find_packages, setup

__version__ = "0.1.3"


def long_description():
    with open("README.md") as f:
        return f.read()


setup(
    name="slh_dsa_botan3",
    version=__version__,
    author="the terrible archivist",
    author_email="info@archive.rip",
    license="GPL-3.0-only",
    packages=find_packages(exclude=["tests"]),
    url="https://gitlab.com/archive-rip/slh_dsa_botan3",
    description="FIPS-205 SLH-DSA bindings for botan3",
    long_description=long_description(),
    long_description_content_type="text/markdown",
    install_requires=["pycryptodome"],
    zip_safe=True,
)
