"""Module for building the package."""

import subprocess
from setuptools import setup, find_packages


def get_version():
    """
    Returns the version based on the git tag.
    """
    try:
        # Run the 'git describe' command to get the current tag
        result = subprocess.run(
            ["git", "describe", "--tags", "--always"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=True,
            text=True
        )
        # Return the version/tag (or full description)
        return result.stdout.strip()
    except subprocess.CalledProcessError:
        return None


NAME = "recursive-matching"
VERSION = get_version()
DESCRIPTION = "Formulating unique assignments recursively."
URL = "https://github.com/JohnMVSantos/Recursive-Matching"
AUTHOR = "John Santos"
AUTHOR_EMAIL = "johnmarisantos@protonmail.com"
LICENSE = "GPL 3.0"

# Read the contents of README file.
with open("../README.md", "r", encoding="utf-8") as f:
    LONG_DESCRIPTION = f.read()

REQUIRED_PACKAGES = [
    "numpy"
]

setup(
    name=NAME,
    version=VERSION,
    description=DESCRIPTION,
    long_description=LONG_DESCRIPTION,
    long_description_content_type="text/markdown",
    url=URL,
    author=AUTHOR,
    author_email=AUTHOR_EMAIL,
    license=LICENSE,
    packages=find_packages(),
    install_requires=REQUIRED_PACKAGES,
    python_requires=">=3.8.0"
)
