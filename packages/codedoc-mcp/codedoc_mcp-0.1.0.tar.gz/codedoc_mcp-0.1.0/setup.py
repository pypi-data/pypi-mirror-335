#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Setup script for CodeDoc MCP package.
"""

from setuptools import setup, find_packages

# 读取版本信息
with open("src/codedoc_mcp/__version__.py", "r") as f:
    exec(f.read())

# 读取README作为长描述
try:
    with open("README.md", "r", encoding="utf-8") as f:
        long_description = f.read()
except FileNotFoundError:
    long_description = "CodeDoc MCP - Code analysis and documentation tool"

setup(
    name="codedoc_mcp",
    version=__version__,
    description="Code analysis and documentation tool with MCP support",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="CodeDoc Team",
    author_email="neozheng2336@gmail.com",
    url="https://github.com/aIFzzf/codedoc_mcp",
    package_dir={"": "src"},
    packages=find_packages(where="src"),
    install_requires=[
        "loguru>=0.6.0",
        "mcp>=1.0.0",
        "regex>=2022.10.31",
        "jinja2>=3.1.2",
        "markdown>=3.4.3",
        "httpx>=0.28.1",
    ],
    entry_points={
        "console_scripts": [
            "codedoc_mcp=codedoc_mcp.__main__:main",
        ],
    },
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Topic :: Software Development :: Documentation",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Software Development :: Code Generators",
    ],
    keywords="code analysis, documentation, markdown, mermaid, diagram",
    python_requires=">=3.8",
    project_urls={
        "Bug Reports": "https://github.com/aIFzzf/codedoc_mcp/issues",
        "Source": "https://github.com/aIFzzf/codedoc_mcp",
        "Documentation": "https://github.com/aIFzzf/codedoc_mcp#readme",
    },
    include_package_data=True,
    zip_safe=False,
)
