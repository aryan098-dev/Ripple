
import ast
from pathlib import Path


def analyze_python_file(file_path):
    """
    Analyze a Python file and extract its
    functions, classes, imports and function calls.
    """

    path = Path(file_path)

    try:
        source_code = path.read_text(encoding="utf-8")
        tree = ast.parse(source_code, filename=str(path))

    except (OSError, UnicodeDecodeError, SyntaxError) as error:
        return {
            "file": str(path),
            "error": str(error),
        }

    functions = []
    classes = []
    imports = []
    calls = []

    for node in ast.walk(tree):

        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            functions.append(node.name)

        elif isinstance(node, ast.ClassDef):
            classes.append(node.name)

        elif isinstance(node, ast.Import):
            for alias in node.names:
                imports.append(alias.name)

        elif isinstance(node, ast.ImportFrom):
            imports.append(node.module or "")

        elif isinstance(node, ast.Call):

            if isinstance(node.func, ast.Name):
                calls.append(node.func.id)

            elif isinstance(node.func, ast.Attribute):
                calls.append(node.func.attr)

    return {
        "file": str(path),
        "functions": sorted(set(functions)),
        "classes": sorted(set(classes)),
        "imports": sorted(set(imports)),
        "calls": sorted(set(calls)),
    }


if __name__ == "__main__":

    target_file = Path(__file__).with_name("git_diff.py")

    result = analyze_python_file(target_file)

    print("\nRipple - Python AST Analyzer")
    print("-" * 35)

    if "error" in result:
        print("Analysis failed:", result["error"])

    else:
        print("File:", result["file"])
        print("Functions:", result["functions"])
        print("Classes:", result["classes"])
        print("Imports:", result["imports"])
        print("Function calls:", result["calls"])
