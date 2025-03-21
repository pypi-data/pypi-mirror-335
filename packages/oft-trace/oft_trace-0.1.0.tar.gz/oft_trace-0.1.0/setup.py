import os
from setuptools import setup, find_packages

# Read the contents of README file
with open(os.path.join(os.path.abspath(os.path.dirname(__file__)), 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name="oft-trace",
    version="0.1.0",
    description="Analyzer and visualizer for OpenFastTrace aspec reports",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Vysakh P PIllai",
    author_email="vysakhpillai@embeddedinn.com",
    url="https://github.com/vppillai/oft-trace",
    packages=find_packages(),
    include_package_data=True,
    python_requires=">=3.7",
    install_requires=[
        "typer>=0.4.0",
        "rich>=10.0.0",
    ],
    entry_points={
        "console_scripts": [
            "oft-trace=oft_trace.cli:main",
        ],
    },
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
)