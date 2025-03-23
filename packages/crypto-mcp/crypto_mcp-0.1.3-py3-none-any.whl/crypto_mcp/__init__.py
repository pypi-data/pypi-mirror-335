"""
Crypto Price MCP - An MCP-based cryptocurrency price query and data analysis tool

This is a cryptocurrency price query server based on the Model Context Protocol (MCP).
It provides various tools to obtain virtual currency prices, market trends, detailed information, and K-line data.
"""

__version__ = "0.1.3"

# 将相对导入改为绝对导入
try:
    from crypto_mcp.crypto_mcp import *
except ImportError:
    pass  # 在安装过程中可能会失败，但不影响版本信息的获取
