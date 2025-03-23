#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Crypto Price MCP 命令行入口
"""

from .crypto_mcp import mcp


def main():
    """启动MCP服务器"""
    print("启动 Crypto Price MCP 服务器...")
    mcp.run(transport="stdio")


if __name__ == "__main__":
    main()
