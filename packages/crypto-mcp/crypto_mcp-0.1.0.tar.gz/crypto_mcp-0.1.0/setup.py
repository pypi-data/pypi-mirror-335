#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import setup, find_packages
import os
import sys

# 获取版本号
about = {}
with open(os.path.join("crypto_mcp", "__init__.py"), "r", encoding="utf-8") as f:
    exec(f.read(), about)

# 读取README文件
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

# 确保Python版本满足要求
if sys.version_info < (3, 7):
    print("Crypto Price MCP 要求 Python 3.7+")
    sys.exit(1)

# 设置依赖项
requirements = [
    "httpx",
    "requests",
    "fastmcp>=0.1.0",
]

setup(
    name="crypto_mcp",
    version=about["__version__"],
    author="Your Name",
    author_email="your.email@example.com",
    description="一个基于MCP的加密货币价格查询服务器",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/crypto_mcp",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: 3.13",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Office/Business :: Financial",
    ],
    python_requires=">=3.7",
    install_requires=requirements,
    entry_points={
        "console_scripts": [
            "crypto_mcp=crypto_mcp.__main__:main",
        ],
    },
)
