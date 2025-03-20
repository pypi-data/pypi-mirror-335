import os
from pathlib import Path


def project_to_markdown(root_path: str) -> str:
    """
    Convert a project's Python files to a markdown format document.
    full code and all will be included
    Each file's path and content will be included in the markdown.

    Args:
        root_path (str): Root directory path of the project

    Returns:
        str: Markdown formatted string containing all Python file paths and their contents
    """
    markdown_content = []

    # Convert to Path object for easier handling
    root = Path(root_path)

    # Walk through all files and directories
    for current_path, dirs, files in os.walk(root):
        # Skip __pycache__ directories
        if '__pycache__' in current_path:
            continue

        for file in files:
            # Only process Python files
            if file.endswith('.py'):
                file_path = Path(current_path) / file
                relative_path = file_path.relative_to(root)

                try:
                    # Read the file content
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()

                    # Add file path and content to markdown
                    markdown_content.append(f"## File: {relative_path}\n")
                    markdown_content.append("```python")
                    markdown_content.append(content)
                    markdown_content.append("```\n")
                except Exception as e:
                    markdown_content.append(f"## File: {relative_path}\n")
                    markdown_content.append(f"Error reading file: {str(e)}\n")

    # Join all content with newlines
    return "\n".join(markdown_content)
