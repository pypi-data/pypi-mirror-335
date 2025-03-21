from setuptools import setup, find_packages
import os
import tomli

def read_requirements(filename):
    with open(filename, "r", encoding="utf-8") as f:
        return [line.strip() for line in f if line.strip() and not line.startswith("#")]

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

# Get version from pyproject.toml
with open("pyproject.toml", "rb") as f:
    pyproject = tomli.load(f)
version = pyproject["project"]["version"]

# Get requirements first
install_requires = read_requirements("requirements.txt")

setup(
    name="linear-mcp",
    version=version,
    description="A Linear API integration for MCP",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/context-labs/linear-mcp",
    packages=find_packages(),
    classifiers=[
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.12",
    ],
    python_requires=">=3.12",
    install_requires=install_requires,
    data_files=[(".", ["requirements.txt"])],
    entry_points={
        "console_scripts": [
            "linear-mcp=linear_mcp.linear:main",
        ],
    },
)