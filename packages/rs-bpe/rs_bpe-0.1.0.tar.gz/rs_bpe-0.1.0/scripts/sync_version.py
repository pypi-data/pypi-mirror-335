#!/usr/bin/env python3
"""
Synchronizes version information between Cargo.toml and Python package.

Key Components:
    update_versions(): Updates versions in both Cargo.toml and Python __init__.py
    bump_version(): Increments version numbers based on semantic versioning

Project Dependencies:
    This file uses: tomllib: To parse Cargo.toml file
    This file is used by: CI/CD pipelines or developers for version management
"""

import argparse
import re
import sys
from pathlib import Path
from typing import Literal

try:
    import tomllib
except ImportError:
    # For Python < 3.11
    import tomli as tomllib


def parse_version(version: str) -> "tuple[int, int, int]":
    """
    Parses a semantic version string into its components.
    
    Parameters
    ----------
    version (str): Version string in format "X.Y.Z"
    
    Returns
    -------
    tuple[int, int, int]: Major, minor, and patch version numbers
    
    Execution Flow:
    1. Splits the version string by periods
    2. Converts each component to an integer
    3. Returns the components as a tuple

    """
    try:
        major, minor, patch = version.split(".")
        return int(major), int(minor), int(patch)
    except ValueError:
        print(f"Error: Invalid version format '{version}'. Expected X.Y.Z")
        sys.exit(1)


def bump_version(
    version: str, bump_type: Literal["major", "minor", "patch"]
) -> str:
    """
    Bumps a version based on semantic versioning rules.
    
    Parameters
    ----------
    version (str): Current version in format "X.Y.Z"
    bump_type (Literal["major", "minor", "patch"]): Type of bump
    
    Returns
    -------
    str: New version in format "X.Y.Z"
    
    Execution Flow:
    1. Parses current version into components
    2. Increments appropriate component based on bump_type
    3. Resets lower components to zero if needed
    4. Returns new version string

    """
    major, minor, patch = parse_version(version)
    
    if bump_type == "major":
        return f"{major + 1}.0.0"
    elif bump_type == "minor":
        return f"{major}.{minor + 1}.0"
    elif bump_type == "patch":
        return f"{major}.{minor}.{patch + 1}"
    else:
        print(f"Error: Invalid bump type '{bump_type}'")
        sys.exit(1)


def get_current_version(cargo_file: str) -> str:
    """
    Gets current version from Cargo.toml file.
    
    Parameters
    ----------
    cargo_file (str): Path to Cargo.toml file
    
    Returns
    -------
    str: Current version string
    
    Execution Flow:
    1. Reads the Cargo.toml file
    2. Parses it as TOML using tomllib
    3. Extracts the version field
    4. Returns the version string

    """
    try:
        cargo_path = Path(cargo_file)
        if not cargo_path.exists():
            print(f"Error: Cargo.toml file not found at {cargo_file}")
            sys.exit(1)
            
        with open(cargo_path, "rb") as f:
            cargo_data = tomllib.load(f)
        
        if "package" not in cargo_data or "version" not in cargo_data["package"]:
            print("Error: Couldn't find package.version in Cargo.toml")
            sys.exit(1)
            
        return cargo_data["package"]["version"]
    except Exception as e:
        print(f"Error reading Cargo.toml: {e}")
        sys.exit(1)


def update_cargo_toml(cargo_file: str, new_version: str) -> None:
    """
    Updates version in Cargo.toml file.
    
    Parameters
    ----------
    cargo_file (str): Path to Cargo.toml file
    new_version (str): New version string to set
    
    Execution Flow:
    1. Reads the Cargo.toml file
    2. Updates the version field using regex
    3. Writes the updated content back to the file

    """
    try:
        with open(cargo_file, "r") as f:
            content = f.read()
        
        # Replace version in package section (at the beginning of the file)
        new_content = re.sub(
            r'(version\s*=\s*["\']).*(["\']\s*)',
            rf'\g<1>{new_version}\g<2>',
            content,
            count=1  # Only replace the first occurrence
        )
        
        with open(cargo_file, "w") as f:
            f.write(new_content)
            
        print(f"Updated {cargo_file} to version {new_version}")
    except Exception as e:
        print(f"Error updating Cargo.toml: {e}")
        sys.exit(1)


def update_python_version(init_file: str, new_version: str) -> None:
    """
    Updates version in Python __init__.py file.
    
    Parameters
    ----------
    init_file (str): Path to __init__.py file
    new_version (str): New version string to set
    
    Execution Flow:
    1. Reads the __init__.py file
    2. Replaces the version string using regex
    3. Writes the updated content back to the file

    """
    try:
        init_path = Path(init_file)
        if not init_path.exists():
            print(f"Error: __init__.py file not found at {init_file}")
            sys.exit(1)
            
        with open(init_file, "r") as f:
            content = f.read()
        
        new_content = re.sub(
            r'__version__\s*=\s*["\'].*["\']',
            f'__version__ = "{new_version}"',
            content
        )
        
        with open(init_file, "w") as f:
            f.write(new_content)
        
        print(f"Updated {init_file} to version {new_version}")
    except Exception as e:
        print(f"Error updating Python version: {e}")
        sys.exit(1)


def update_versions(
    cargo_file: str,
    init_file: str,
    bump_type: Literal["major", "minor", "patch"] | None = None,
    set_version: str | None = None
) -> None:
    """
    Updates versions in both Cargo.toml and Python package.
    
    Parameters
    ----------
    cargo_file (str): Path to Cargo.toml file
    init_file (str): Path to __init__.py file
    bump_type (Literal["major", "minor", "patch"] | None): Type of bump
    set_version (str | None): Specific version to set
    
    Execution Flow:
    1. Gets current version from Cargo.toml
    2. Determines new version based on arguments
    3. Updates both files with the new version

    """
    current_version = get_current_version(cargo_file)
    print(f"Current version: {current_version}")
    
    if set_version:
        # Validate the provided version
        try:
            parse_version(set_version)
            new_version = set_version
        except SystemExit:
            print("Error: Please provide a valid version in X.Y.Z format")
            sys.exit(1)
    elif bump_type:
        new_version = bump_version(current_version, bump_type)
    else:
        print("No version change requested. Using current version.")
        new_version = current_version
    
    if new_version != current_version:
        print(f"Setting version to: {new_version}")
        update_cargo_toml(cargo_file, new_version)
        update_python_version(init_file, new_version)
        print("Version synchronized successfully!")
    else:
        print("Version unchanged.")


def main() -> None:
    """
    Main entry point for the script.
    
    Execution Flow:
    1. Sets up argument parser with options for version management
    2. Parses command line arguments
    3. Calls update_versions with the provided arguments
    """
    parser = argparse.ArgumentParser(
        description="Synchronize version between Cargo.toml and Python package"
    )
    
    version_group = parser.add_mutually_exclusive_group()
    version_group.add_argument(
        "--bump",
        choices=["major", "minor", "patch"],
        help="Bump version (major, minor, or patch)"
    )
    version_group.add_argument(
        "--set",
        dest="set_version",
        help="Set specific version (format: X.Y.Z)"
    )
    
    parser.add_argument(
        "--cargo",
        default="Cargo.toml",
        help="Path to Cargo.toml file (default: Cargo.toml)"
    )
    parser.add_argument(
        "--init",
        default="python/rs_bpe/__init__.py",
        help="Path to Python __init__.py file (default: python/rs_bpe/__init__.py)"
    )
    
    args = parser.parse_args()
    
    update_versions(
        args.cargo,
        args.init,
        args.bump,
        args.set_version
    )


if __name__ == "__main__":
    main()
