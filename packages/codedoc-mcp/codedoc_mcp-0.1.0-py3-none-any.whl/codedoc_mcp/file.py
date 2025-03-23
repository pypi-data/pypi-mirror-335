#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
File handling module for CodeDoc MCP Server.
This module provides functionality to process code files and generate documentation.
"""

# Import built-in modules
import os
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

# Import third-party modules
from loguru import logger
from mcp.server.fastmcp import Context

# Import local modules
from codedoc_mcp.app import mcp
from codedoc_mcp.errors import ErrorCode
from codedoc_mcp.errors import CodeDocError
from codedoc_mcp.generator.markdown_generator import MarkdownGenerator
from codedoc_mcp.generator.mermaid_generator import MermaidGenerator
from codedoc_mcp.parser.base_parser import BaseParser
from codedoc_mcp.parser.python_parser import PythonParser
from codedoc_mcp.parser.csharp_parser import CSharpParser
from codedoc_mcp.parser.cpp_parser import CppParser
from codedoc_mcp.parser.javascript_parser import JavaScriptParser
from codedoc_mcp.parser.shader_parser import ShaderParser


def get_parser_for_file(file_path: str) -> BaseParser:
    """
    Get the appropriate parser for a given file based on its extension.

    Args:
        file_path: Path to the code file.

    Returns:
        BaseParser: An instance of the appropriate parser.

    Raises:
        CodeDocError: If the file type is not supported.
    """
    file_ext = Path(file_path).suffix.lower()
    
    if file_ext == '.py':
        return PythonParser(file_path)
    elif file_ext == '.cs':
        return CSharpParser(file_path)
    elif file_ext in ['.cpp', '.h', '.hpp', '.cc']:
        return CppParser(file_path)
    elif file_ext in ['.js', '.jsx', '.ts', '.tsx']:
        return JavaScriptParser(file_path)
    elif file_ext in ['.shader', '.compute', '.cginc', '.hlsl']:
        return ShaderParser(file_path)
    else:
        raise CodeDocError(f"Unsupported file type: {file_ext}", ErrorCode.VALIDATION_ERROR)


@mcp.tool()
async def analyze_code_file(
    file_path: str,
    output_dir: str = "docs",
    generate_markdown: bool = True,
    generate_class_diagram: bool = True,
    generate_flow_diagram: bool = False,
    generate_structure_diagram: bool = False,
    ctx: Optional[Context] = None
) -> Dict[str, Any]:
    """
    Analyze a code file and generate documentation.

    Args:
        file_path: Path to the code file to analyze.
        output_dir: Directory to save generated documentation files.
        generate_markdown: Whether to generate Markdown documentation.
        generate_class_diagram: Whether to generate a Mermaid class diagram.
        generate_flow_diagram: Whether to generate a Mermaid flow diagram.
        generate_structure_diagram: Whether to generate a Mermaid structure diagram.
        ctx: FastMCP context.

    Returns:
        Dict[str, Any]: A dictionary containing paths to generated files and parsed data.

    Raises:
        CodeDocError: If the file cannot be processed.
    """
    try:
        if ctx:
            await ctx.report_progress(0.1)
            await ctx.info(f"Analyzing file: {file_path}")
        
        # Validate file path
        if not os.path.exists(file_path):
            error_msg = f"File not found: {file_path}"
            logger.error(error_msg)
            if ctx:
                await ctx.error(error_msg)
            raise CodeDocError(error_msg, ErrorCode.FILE_NOT_FOUND)
        
        # Get appropriate parser
        parser = get_parser_for_file(file_path)
        
        if ctx:
            await ctx.report_progress(0.3)
            await ctx.info("Parsing file...")
        
        # Parse the file
        parsed_data = parser.parse()
        
        if ctx:
            await ctx.report_progress(0.5)
            await ctx.info("Generating documentation...")
        
        # Generate documentation
        result = {
            "file_path": file_path,
            "parsed_data": parsed_data,
            "generated_files": []
        }
        
        # Create file name base
        file_name_base = os.path.splitext(os.path.basename(file_path))[0]
        
        # Generate Markdown documentation
        if generate_markdown:
            markdown_generator = MarkdownGenerator(output_dir)
            markdown_file = f"{file_name_base}_documentation.md"
            markdown_path = markdown_generator.generate(parsed_data, markdown_file)
            result["generated_files"].append({
                "type": "markdown",
                "path": markdown_path
            })
            
            if ctx:
                await ctx.info(f"Generated Markdown documentation: {markdown_path}")
        
        # Generate Mermaid diagrams
        mermaid_generator = MermaidGenerator(output_dir)
        
        if generate_class_diagram:
            class_diagram_file = f"{file_name_base}_class_diagram.md"
            class_diagram_path = mermaid_generator.generate_class_diagram(parsed_data, class_diagram_file)
            result["generated_files"].append({
                "type": "class_diagram",
                "path": class_diagram_path
            })
            
            if ctx:
                await ctx.info(f"Generated class diagram: {class_diagram_path}")
        
        if generate_flow_diagram:
            flow_diagram_file = f"{file_name_base}_flow_diagram.md"
            flow_diagram_path = mermaid_generator.generate_flow_diagram(parsed_data, flow_diagram_file)
            result["generated_files"].append({
                "type": "flow_diagram",
                "path": flow_diagram_path
            })
            
            if ctx:
                await ctx.info(f"Generated flow diagram: {flow_diagram_path}")
        
        if generate_structure_diagram:
            structure_diagram_file = f"{file_name_base}_structure_diagram.md"
            structure_diagram_path = mermaid_generator.generate_structure_diagram(parsed_data, structure_diagram_file)
            result["generated_files"].append({
                "type": "structure_diagram",
                "path": structure_diagram_path
            })
            
            if ctx:
                await ctx.info(f"Generated structure diagram: {structure_diagram_path}")
        
        if ctx:
            await ctx.report_progress(1.0)
            await ctx.info("Analysis complete!")
        
        return result
        
    except Exception as e:
        error_msg = f"Error analyzing file: {str(e)}"
        logger.error(error_msg)
        if ctx:
            await ctx.error(error_msg)
        if isinstance(e, CodeDocError):
            raise
        raise CodeDocError(error_msg, ErrorCode.UNKNOWN_ERROR) from e


@mcp.tool()
async def analyze_directory(
    directory_path: str,
    output_dir: str = "docs",
    file_extensions: List[str] = None,
    recursive: bool = True,
    generate_markdown: bool = True,
    generate_class_diagram: bool = True,
    ctx: Optional[Context] = None
) -> Dict[str, Any]:
    """
    Analyze all code files in a directory and generate documentation.

    Args:
        directory_path: Path to the directory containing code files.
        output_dir: Directory to save generated documentation files.
        file_extensions: List of file extensions to include (e.g., ['.py', '.cs']).
        recursive: Whether to search subdirectories recursively.
        generate_markdown: Whether to generate Markdown documentation.
        generate_class_diagram: Whether to generate Mermaid class diagrams.
        ctx: FastMCP context.

    Returns:
        Dict[str, Any]: A dictionary containing paths to generated files and summary information.

    Raises:
        CodeDocError: If the directory cannot be processed.
    """
    try:
        if ctx:
            await ctx.report_progress(0.1)
            await ctx.info(f"Analyzing directory: {directory_path}")
        
        # Validate directory path
        if not os.path.isdir(directory_path):
            error_msg = f"Directory not found: {directory_path}"
            logger.error(error_msg)
            if ctx:
                await ctx.error(error_msg)
            raise CodeDocError(error_msg, ErrorCode.FILE_NOT_FOUND)
        
        # Default file extensions if none provided
        if file_extensions is None:
            file_extensions = ['.py', '.cs', '.cpp', '.h', '.hpp', '.js', '.jsx', '.ts', '.tsx', '.shader']
        
        # Find all matching files
        files_to_analyze = []
        if recursive:
            for root, _, files in os.walk(directory_path):
                for file in files:
                    if any(file.endswith(ext) for ext in file_extensions):
                        files_to_analyze.append(os.path.join(root, file))
        else:
            for file in os.listdir(directory_path):
                file_path = os.path.join(directory_path, file)
                if os.path.isfile(file_path) and any(file.endswith(ext) for ext in file_extensions):
                    files_to_analyze.append(file_path)
        
        if not files_to_analyze:
            if ctx:
                await ctx.info("No matching files found.")
            return {
                "directory_path": directory_path,
                "analyzed_files": [],
                "generated_files": []
            }
        
        # Analyze each file
        analyzed_files = []
        generated_files = []
        total_files = len(files_to_analyze)
        
        for i, file_path in enumerate(files_to_analyze):
            if ctx:
                progress = 0.1 + 0.9 * (i / total_files)
                await ctx.report_progress(progress)
                await ctx.info(f"Analyzing file {i+1}/{total_files}: {file_path}")
            
            try:
                result = await analyze_code_file(
                    file_path=file_path,
                    output_dir=output_dir,
                    generate_markdown=generate_markdown,
                    generate_class_diagram=generate_class_diagram,
                    generate_flow_diagram=False,
                    generate_structure_diagram=False
                )
                
                analyzed_files.append({
                    "file_path": file_path,
                    "status": "success"
                })
                
                generated_files.extend(result["generated_files"])
                
            except Exception as e:
                logger.error(f"Error analyzing file {file_path}: {str(e)}")
                analyzed_files.append({
                    "file_path": file_path,
                    "status": "error",
                    "error": str(e)
                })
        
        if ctx:
            await ctx.report_progress(1.0)
            await ctx.info(f"Analysis complete! Analyzed {len(analyzed_files)} files.")
        
        return {
            "directory_path": directory_path,
            "analyzed_files": analyzed_files,
            "generated_files": generated_files
        }
        
    except Exception as e:
        error_msg = f"Error analyzing directory: {str(e)}"
        logger.error(error_msg)
        if ctx:
            await ctx.error(error_msg)
        if isinstance(e, CodeDocError):
            raise
        raise CodeDocError(error_msg, ErrorCode.UNKNOWN_ERROR) from e
