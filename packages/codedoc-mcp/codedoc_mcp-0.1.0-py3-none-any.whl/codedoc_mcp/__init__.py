"""CodeDoc MCP Server.

This module provides a FastMCP server for CodeDoc functionality.
It exposes tools for code analysis, documentation generation, and visualization.
"""

# Import built-in modules
import os
import sys

# 确保当前目录在路径中，便于相对导入
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import local modules
from __version__ import __version__
from codedoc_mcp.app import mcp, APP_NAME
from codedoc_mcp.errors import CodeDocError, ErrorCode

# 导入解析器
from codedoc_mcp.parser.base_parser import BaseParser
from codedoc_mcp.parser.python_parser import PythonParser
from codedoc_mcp.parser.csharp_parser import CSharpParser
from codedoc_mcp.parser.cpp_parser import CppParser
from codedoc_mcp.parser.javascript_parser import JavaScriptParser
from codedoc_mcp.parser.shader_parser import ShaderParser

# 导入生成器
from codedoc_mcp.generator.markdown_generator import MarkdownGenerator
from codedoc_mcp.generator.mermaid_generator import MermaidGenerator

# 导入MCP工具
from codedoc_mcp.file import analyze_code_file, analyze_directory

# 暴露主要API
__all__ = [
    "__version__",
    "APP_NAME",
    "mcp",
    "CodeDocError",
    "ErrorCode",
    "BaseParser",
    "PythonParser",
    "CSharpParser",
    "CppParser",
    "JavaScriptParser",
    "ShaderParser",
    "MarkdownGenerator",
    "MermaidGenerator",
    "analyze_code_file",
    "analyze_directory"
]
