"""
Setup script for rs_bpe-stubs package.
"""

from setuptools import setup

setup(
    name="rs_bpe-stubs",
    version="0.1.0",
    description="Type stubs for rs_bpe",
    author="gweidart",
    author_email="gweidart@gmail.com",
    packages=["rs_bpe-stubs"],
    package_data={"rs_bpe-stubs": ["py.typed", "*.pyi"]},
    zip_safe=False,  # Required for mypy to find the package
    python_requires=">=3.7",
)
