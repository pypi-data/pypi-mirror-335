from setuptools import setup, find_packages
import re
from pathlib import Path

def read_requirements(file):
    """Read requirements file and return a list of dependencies"""
    with open(file, encoding="utf-8") as f:
        return f.read().splitlines()

def read_file(file):
    """Read a file and return its content."""
    with open(file, encoding="utf-8") as f:
        return f.read().strip()

def get_version():
    """Get the version from __init__.py"""
    init_file = Path("helpr/__init__.py").read_text()
    version_match = re.search(r"^__version__ = ['\"]([^'\"]*)['\"]", init_file, re.M)
    if version_match:
        return version_match.group(1)
    raise RuntimeError("Version string not found in __init__.py")

# Read metadata files
long_description = read_file("README.rst")
requirements = read_requirements("requirements.txt")
version = get_version()

setup(
    name="helpr",
    version=version,
    author="Clinikally",
    author_email="puneetsrivastava@clinikally.com",
    url="https://github.com/clinikally/helpr",
    description="A Python package to help you with your daily tasks",
    long_description=long_description,
    long_description_content_type="text/x-rst",
    license="MIT license",
    packages=find_packages(exclude=["tests", "docs"]),
    install_requires=requirements,
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
)