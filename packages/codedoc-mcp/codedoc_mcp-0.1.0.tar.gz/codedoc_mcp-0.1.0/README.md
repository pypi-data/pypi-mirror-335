# CodeDoc MCP

CodeDoc MCP是一个强大的代码分析和文档生成工具，支持多种编程语言，能够自动生成Markdown文档和Mermaid图表。

## 功能特点

- **多语言支持**：支持Python、C#、C++、JavaScript和Unity着色器等多种编程语言
- **文档生成**：自动生成详细的Markdown格式文档
- **图表生成**：生成Mermaid格式的类图、流程图和结构图
- **MCP服务**：提供MCP服务器接口，方便集成到其他工具中
- **批量处理**：支持对整个目录进行批量分析和文档生成

## 安装方法

```bash
pip install codedoc_mcp
```

## 快速开始

### 命令行使用

```bash
# 分析单个文件
codedoc_mcp analyze --file path/to/your/file.py --output docs

# 分析整个目录
codedoc_mcp analyze-dir --dir path/to/your/project --output docs
```

### Python代码中使用

```python
from codedoc_mcp import analyze_code_file, analyze_directory

# 分析单个文件
result = analyze_code_file(
    file_path="path/to/your/file.py",
    output_dir="docs",
    generate_markdown=True,
    generate_class_diagram=True
)

# 分析整个目录
result = analyze_directory(
    directory_path="path/to/your/project",
    output_dir="docs",
    file_extensions=[".py", ".cs"],
    recursive=True
)
```

## 支持的文件类型

- Python (.py)
- C# (.cs)
- C++ (.cpp, .h, .hpp, .cc)
- JavaScript/TypeScript (.js, .jsx, .ts, .tsx)
- Unity着色器 (.shader, .compute, .cginc, .hlsl)

## 文档示例

### 生成的Markdown文档

生成的Markdown文档包含以下内容：

- 类和接口的详细描述
- 方法和函数的参数、返回值和文档字符串
- 属性和字段的类型和描述
- 继承关系和依赖关系

### 生成的Mermaid图表

生成的Mermaid图表包括：

- 类图：展示类之间的继承和关联关系
- 流程图：展示函数调用流程
- 结构图：展示项目结构和模块依赖关系

## 许可证

MIT