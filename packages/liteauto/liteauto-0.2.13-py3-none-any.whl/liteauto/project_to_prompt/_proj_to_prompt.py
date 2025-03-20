import os
import ast
import shutil
import tempfile
from typing import Optional, Dict, List
from urllib.parse import urlparse

from git import Repo


class ProjectToPrompt:
    def __init__(self, project_path: str):
        """
        Initialize the analyzer with project path or GitHub URL.

        Args:
            project_path (str): Path to the Python project directory or GitHub repository URL
        """
        self.original_path = project_path
        self.temp_dir = None

        if self._is_github_url(project_path):
            self.project_path = self._clone_github_repo(project_path)
        else:
            self.project_path = project_path

    def _is_github_url(self, path: str) -> bool:
        """
        Check if the provided path is a GitHub URL.

        Args:
            path (str): Path or URL to check

        Returns:
            bool: True if path is a GitHub URL, False otherwise
        """
        try:
            parsed = urlparse(path)
            return parsed.netloc in ['github.com', 'www.github.com']
        except:
            return False

    def _clone_github_repo(self, github_url: str) -> str:
        """
        Clone a GitHub repository to a temporary directory.

        Args:
            github_url (str): GitHub repository URL

        Returns:
            str: Path to the cloned repository
        """
        self.temp_dir = tempfile.mkdtemp()
        try:
            Repo.clone_from(github_url, self.temp_dir)
            return self.temp_dir
        except Exception as e:
            shutil.rmtree(self.temp_dir)
            raise Exception(f"Failed to clone repository: {str(e)}")

    def __del__(self):
        """
        Cleanup temporary directory if it exists.
        """
        if self.temp_dir and os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)

    def get_python_files(self) -> List[str]:
        """
        Recursively get all Python files in the project.

        Returns:
            List[str]: List of Python file paths
        """
        python_files = []
        for root, _, files in os.walk(self.project_path):
            for file in files:
                if file.endswith('.py'):
                    python_files.append(os.path.join(root, file))
        return python_files

    def analyze_file(self, file_path: str) -> Dict:
        """
        Analyze a single Python file and extract its components.

        Args:
            file_path (str): Path to the Python file

        Returns:
            Dict: Dictionary containing imports, classes, and functions
        """
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read()

        try:
            tree = ast.parse(content)
        except:
            return {"imports": [], "classes": [], "functions": []}

        analysis = {
            "imports": [],
            "classes": [],
            "functions": []
        }

        for node in ast.walk(tree):
            # Get imports
            if isinstance(node, (ast.Import, ast.ImportFrom)):
                if isinstance(node, ast.Import):
                    for name in node.names:
                        analysis["imports"].append(name.name)
                else:
                    module = node.module if node.module else ''
                    for name in node.names:
                        analysis["imports"].append(f"{module}.{name.name}")

            # Get classes
            elif isinstance(node, ast.ClassDef):
                docstring = ast.get_docstring(node)
                analysis["classes"].append({
                    "name": node.name,
                    "docstring": docstring
                })

            # Get functions
            elif isinstance(node, ast.FunctionDef):
                docstring = ast.get_docstring(node)
                args = [arg.arg for arg in node.args.args]
                analysis["functions"].append({
                    "name": node.name,
                    "args": args,
                    "docstring": docstring
                })

        return analysis

    def generate_markdown(self) -> str:
        """
        Generate markdown documentation for the entire project.

        Returns:
            str: Markdown formatted string of the project documentation
        """
        markdown = "# Project Documentation\n\n"

        for file_path in self.get_python_files():
            relative_path = os.path.relpath(file_path, self.project_path)
            markdown += f"## {relative_path}\n\n"

            analysis = self.analyze_file(file_path)

            # Add imports section
            if analysis["imports"]:
                markdown += "### Imports\n\n"
                for imp in analysis["imports"]:
                    markdown += f"- `{imp}`\n"
                markdown += "\n"

            # Add classes section
            if analysis["classes"]:
                markdown += "### Classes\n\n"
                for cls in analysis["classes"]:
                    markdown += f"#### {cls['name']}\n\n"
                    if cls["docstring"]:
                        markdown += f"{cls['docstring']}\n\n"

            # Add functions section
            if analysis["functions"]:
                markdown += "### Functions\n\n"
                for func in analysis["functions"]:
                    args_str = ", ".join(func["args"])
                    markdown += f"#### {func['name']}({args_str})\n\n"
                    if func["docstring"]:
                        markdown += f"{func['docstring']}\n\n"

            markdown += "---\n\n"

        return markdown

def project_to_prompt(path:str):
    """takes path of directory/project and returns that in prompt format for llm like funcitonand classes names
    params with docstrings level only not full code and return it as full prompt version of code base"""
    obj = ProjectToPrompt(path)
    return obj.generate_markdown()