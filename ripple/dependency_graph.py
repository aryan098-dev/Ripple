
import ast
from pathlib import Path
from collections import defaultdict


def get_module_name(file_path, root_path):
    """Convert a Python file path into a module name."""

    relative_path = file_path.relative_to(root_path)

    parts = list(relative_path.with_suffix("").parts)

    if parts[-1] == "__init__":
        parts.pop()

    return ".".join(parts)


def collect_python_files(root_path):
    """Collect Python files while ignoring virtual environments."""

    ignored_dirs = {
        ".venv",
        "venv",
        "__pycache__",
        ".git",
        "site-packages",
    }

    python_files = []

    for path in root_path.rglob("*.py"):
        if any(part in ignored_dirs for part in path.parts):
            continue

        python_files.append(path)

    return sorted(python_files)


def extract_imports(file_path, root_path):
    """Extract module imports from a Python file."""

    try:
        source = file_path.read_text(encoding="utf-8")
        tree = ast.parse(source, filename=str(file_path))

    except (OSError, UnicodeDecodeError, SyntaxError):
        return []

    imports = []

    current_module = get_module_name(file_path, root_path)

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
                package = package[:len(package) - remove_count]

                if node.module:
                    package.extend(node.module.split("."))

                module_name = ".".join(package)

            else:
                module_name = node.module or ""

            if module_name:
                imports.append(module_name)

    return sorted(set(imports))



def build_dependency_graph(repo_path="."):
    """
    Build a dependency graph.

    Edges point from dependency to dependent.
    """

    root_path = Path(repo_path).resolve()

    python_files = collect_python_files(root_path)

    module_map = {
        get_module_name(path, root_path): path
        for path in python_files
    }

    graph = defaultdict(set)

    for module_name in module_map:
        graph[module_name]

    for file_path in python_files:

        source_module = get_module_name(file_path, root_path)

        imports = extract_imports(file_path, root_path)

        for imported_module in imports:

            matching_modules = [
                name for name in module_map
                if (
                    imported_module == name
                    or imported_module.startswith(name + ".")
                    or name.startswith(imported_module + ".")
                    or name.rsplit(".", 1)[-1] == imported_module
                )
            ]

            for dependency in matching_modules:

                if dependency != source_module:
                    graph[dependency].add(source_module)

    return {
        module: sorted(dependents)
        for module, dependents in sorted(graph.items())
    }



if __name__ == "__main__":

    graph = build_dependency_graph()

    print("\nRipple - Dependency Graph Engine")
    print("-" * 40)

    total_edges = 0

    for module, dependents in graph.items():

        print(f"\n{module}")

        if dependents:
            for dependent in dependents:
                print(f"  └── affects: {dependent}")
                total_edges += 1
        else:
            print("  └── No dependents detected")

    print("\nGraph Summary")
    print("-" * 40)
    print("Total modules:", len(graph))
    print("Total dependency relationships:", total_edges)
