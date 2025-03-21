import os
import re
from setuptools import setup, find_packages

def get_version():
    # Read the version from _version.py
    with open(os.path.join("UEQanalyzer", "_version.py"), "r") as f:
        version_file = f.read()
    version_match = re.search(r'^__version__ = ["\']([^"\']*)["\']', version_file, re.M)
    if version_match:
        return version_match.group(1)
    raise RuntimeError("Unable to find version string.")

# Read the README.md file for the long description
with open("README.md", "r", encoding="utf-8") as f:
    long_description = f.read()

setup(
    name="UEQanalyzer",
    version=get_version(),  # Use the version from _version.py
    description="A Python package for analyzing and visualizing User Experience Questionnaire (UEQ) data.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Pranjali Barve",  # Replace with your name or organization
    url="https://github.com/Pranj99/UEQAnalysis",  # Replace with your project URL
    license="MIT",  # Replace with your license type
    packages=find_packages(),
    install_requires=[
        "pandas",
        "matplotlib",
        "openpyxl",  # Required for reading Excel files
    ],
    entry_points={
        "console_scripts": [
            "ueqanalyzer=cli:main",  # Correct entry point for cli.py at the root
        ],
    },
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",  # Specify the minimum Python version required
)