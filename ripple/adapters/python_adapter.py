
import ast
from pathlib import Path

from ripple.adapters.base import LanguageAdapter
from ripple.ast_analyzer import analyze_python_file


class PythonAdapter(LanguageAdapter):
    """Language adapter for Python projects."""

    def supports(self, file_path: Path) -> bool:
        return file_path.suffix.lower() == ".py"

    def extract_imports(
        self,
        file_path: Path,
        root_path: Path
    ) -> list[str]:

        try:
            source = file_path.read_text(encoding="utf-8")
            tree = ast.parse(source, filename=str(file_path))

        except (OSError, UnicodeDecodeError, SyntaxError):
            return []

        relative_path = file_path.relative_to(root_path)
        parts = list(relative_path.with_suffix("").parts)

        if parts[-1] == "__init__":
            parts.pop()

        current_module = ".".join(parts)
        imports = []

        for node in ast.walk(tree):

            if isinstance(node, ast.Import):
                for alias in node.names:
                    imports.append(alias.name)

            elif isinstance(node, ast.ImportFrom):

                if node.level > 0:
                    package = current_module.split(".")[:-1]

                    if file_path.name == "__init__.py":
                        package = current_module.split(".")

                    remove_count = node.level - 1

                    if remove_count:
                        package = package[:-remove_count]

                    if node.module:
                        package.extend(node.module.split("."))

                    module_name = ".".join(package)

                else:
                    module_name = node.module or ""

                if module_name:
                    imports.append(module_name)

        return sorted(set(imports))

    def extract_symbols(self, file_path: Path) -> dict:
        result = analyze_python_file(file_path)

        if result.get("error"):
            return {}

        return {
            "functions": result.get("functions", []),
            "classes": result.get("classes", []),
        }

    def discover_tests(self, root_path: Path) -> list[Path]:

        ignored_dirs = {
            ".git",
            ".venv",
            "venv",
            "__pycache__",
            "site-packages",
        }

        test_files = []

        for path in root_path.rglob("*.py"):

            relative_parts = path.relative_to(root_path).parts

            if any(part in ignored_dirs for part in relative_parts):
                continue

            if (
                path.name.startswith("test_")
                or path.name.endswith("_test.py")
                or "tests" in relative_parts
            ):
                test_files.append(path)

        return sorted(set(test_files))
