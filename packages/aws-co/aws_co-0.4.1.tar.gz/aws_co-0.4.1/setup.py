from setuptools import setup, find_packages
import os
from pathlib import Path

# Read the contents of README.md
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text()

# Get version from aws_co/__init__.py
with open(Path(this_directory) / "aws_co" / "__init__.py", "r") as f:
    for line in f:
        if line.startswith("__version__"):
            version = line.split("=")[1].strip().strip('"').strip("'")
            break

setup(
    name="aws-co",
    version=version,
    packages=find_packages(exclude=["finders", "finders.*"]),
    include_package_data=True,
    install_requires=[
        "click>=8.0.0",
    ],
    entry_points={
        "console_scripts": [
            "aws-co=aws_co.cli:main",
        ],
    },
    author="David Schwartz",
    author_email="example@example.com",
    description="A CLI tool to assume AWS roles and run commands in target accounts",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/trilogy-group/aws-co",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: System Administrators",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Topic :: System :: Systems Administration",
        "Topic :: Utilities",
    ],
    keywords="aws, cli, role, assume, credentials, iam, sts",
    python_requires=">=3.6",
    project_urls={
        "Bug Reports": "https://github.com/trilogy-group/aws-co/issues",
        "Source": "https://github.com/trilogy-group/aws-co",
    },
)
