#!/usr/bin/env python
"""
This is a wrapper around Maturin build system to enable compatibility
with tools that don't yet support PEP 517/518.

Simply use `pip install .` or run `python setup.py install`.
"""
import os
import re
import subprocess
import sys

from setuptools import setup

# When run as a script, this will call maturin build
if __name__ == "__main__":
    # Direct users to use maturin
    print("This package should be built using Maturin.")
    print("If maturin is not available, it will be installed now.")
    
    # Try to use maturin if installed directly
    try:
        import maturin  # noqa: F401
        print("Maturin already installed, proceeding with build...")
    except ImportError:
        print("Installing Maturin...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "maturin>=1.8,<2.0"])
    
    # Call maturin to build the package
    print("Building with Maturin...")
    # Use a separate process to run maturin build
    subprocess.check_call(["maturin", "build", "--release"])
    
    print("Build complete. Running setup for metadata only...")


def update_version_in_init():
    """
    Updates the version in __init__.py based on environment variable.
    
    Execution Flow:
    1. Reads environment variable VERSION, defaults to Cargo.toml version if not set
    2. Updates the __init__.py file with the new version
    3. Returns the updated version string
    """
    version_file = os.path.join(os.path.dirname(__file__), 'python', 'rs_bpe', '__init__.py')
    
    # Get version from environment or use default from Cargo.toml
    new_version = os.environ.get('VERSION', None)
    
    if new_version:
        with open(version_file, 'r') as f:
            content = f.read()
            
        # Replace version string in __init__.py
        content_new = re.sub(r'__version__ = ["\'].*["\']', f'__version__ = "{new_version}"', content)
        
        with open(version_file, 'w') as f:
            f.write(content_new)
        
        return new_version
    else:
        # If no environment variable, read version from __init__.py
        with open(version_file, 'r') as f:
            for line in f:
                if line.startswith('__version__'):
                    delim = '"' if '"' in line else "'"
                    return line.split(delim)[1]
        
        # If no version found, use default
        return "0.1.0"


# Actual setuptools setup runs only for metadata
# This section is also used by tools like `pip install -e .`
setup(
    name="rs_bpe",
    version=update_version_in_init(),
    description="A rediculously fast Python BPE (Byte Pair Encoder) written in Rust",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    author="gweidart",
    author_email="gweidart@gmail.com",
    url="https://github.com/gweidart/rs-bpe",
    license="MIT",
    python_requires=">=3.8",
    packages=["rs_bpe"],
    package_dir={"": "python"},
    package_data={"rs_bpe": ["py.typed", "*.pyi"]},
    zip_safe=False,  # Required for mypy to find the type hints
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: Implementation :: CPython",
        "Programming Language :: Python :: Implementation :: PyPy",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: 3.13",
        "Programming Language :: Rust",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Topic :: Text Processing :: Linguistic",
        "Typing :: Typed",
    ],
    keywords=["bpe", "tokenizer", "nlp", "openai", "embeddings", "rust"],
)
