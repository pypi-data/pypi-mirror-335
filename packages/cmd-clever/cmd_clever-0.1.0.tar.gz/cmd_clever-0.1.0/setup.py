import os
from setuptools import setup, find_packages

# Get the version from the package
about = {}
with open(os.path.join(os.path.dirname(__file__), "cmdclever", "__init__.py")) as f:
    exec(f.read(), about)

# Read the README file for the long description
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="cmd-clever",
    version=about["__version__"],
    description="A command-line tool for generating terminal commands using AI",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Cmd Clever Team",
    author_email="example@example.com",
    url="https://github.com/yourusername/cmd-clever",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.7",
    install_requires=[
        "agno",
    ],
    entry_points={
        "console_scripts": [
            "cmd-clever=cmdclever.cli.main:main",
        ],
    },
) 