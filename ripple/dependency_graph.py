
from collections import defaultdict
from pathlib import Path

from ripple.adapters.registry import create_default_registry


IGNORED_DIRS = {
    ".git",
    ".venv",
    "venv",
    "__pycache__",
    "site-packages",
    "node_modules",
    "dist",
    "build",
    ".next",
}


def get_module_name(file_path, root_path):
    """Preserve the existing Python module naming convention."""

    relative_path = file_path.relative_to(root_path)
    parts = list(relative_path.with_suffix("").parts)

    if parts[-1] == "__init__":
        parts.pop()

    return ".".join(parts)


def collect_supported_files(root_path):
    """Collect files supported by registered language adapters."""

    registry = create_default_registry()
    supported_files = []

    for path in root_path.rglob("*"):

        if not path.is_file():
            continue

        relative_parts = path.relative_to(root_path).parts

        if any(part in IGNORED_DIRS for part in relative_parts):
            continue

        if registry.get_adapter(path):
            supported_files.append(path)

    return sorted(supported_files)


def get_file_module_id(file_path, root_path, adapter):
    """Generate a unique identifier for a source file."""

    if adapter.__class__.__name__ == "PythonAdapter":
        return get_module_name(file_path, root_path)

    relative_path = file_path.relative_to(root_path)
    module_name = ".".join(relative_path.with_suffix("").parts)

    return f"javascript:{module_name}"


def resolve_javascript_import(import_path, source_file, root_path):
    """Resolve relative JavaScript imports to project files."""

    if not import_path.startswith("."):
        return None

    target = (source_file.parent / import_path).resolve()

    candidates = [
        target,
        *[
            target.with_suffix(extension)
            for extension in (".js", ".jsx", ".mjs", ".cjs")
        ],
        *[
            target / f"index{extension}"
            for extension in (".js", ".jsx", ".mjs", ".cjs")
        ],
    ]

    for candidate in candidates:

        if not candidate.is_file():
            continue

        try:
            return candidate.relative_to(root_path).as_posix()
        except ValueError:
            continue

    return None


def build_dependency_graph(repo_path="."):
    """
    Build a unified dependency graph.

    Edges point from dependency to dependent.
    Supports all registered language adapters.
    """

    root_path = Path(repo_path).resolve()
    registry = create_default_registry()

    supported_files = collect_supported_files(root_path)

    file_map = {}

    for file_path in supported_files:

        adapter = registry.get_adapter(file_path)

        module_id = get_file_module_id(
            file_path,
            root_path,
            adapter
        )

        file_map[file_path] = module_id

    graph = defaultdict(set)

    for module_id in file_map.values():
        graph[module_id]

    for file_path, source_module in file_map.items():

        adapter = registry.get_adapter(file_path)

        imports = adapter.extract_imports(
            file_path,
            root_path
        )

        for imported_module in imports:

            dependency_ids = set()

            if adapter.__class__.__name__ == "JavaScriptAdapter":

                resolved_path = resolve_javascript_import(
                    imported_module,
                    file_path,
                    root_path
                )

                if resolved_path:

                    for candidate, module_id in file_map.items():

                        if (
                            candidate.relative_to(root_path).as_posix()
                            == resolved_path
                        ):
                            dependency_ids.add(module_id)

            else:

                for module_id in file_map.values():

                    if (
                        imported_module == module_id
                        or imported_module.startswith(module_id + ".")
                        or module_id.startswith(imported_module + ".")
                        or module_id.rsplit(".", 1)[-1] == imported_module
                    ):
                        dependency_ids.add(module_id)

            for dependency_id in dependency_ids:

                if dependency_id != source_module:
                    graph[dependency_id].add(source_module)

    return {
        module: sorted(dependents)
        for module, dependents in sorted(graph.items())
    }


if __name__ == "__main__":

    graph = build_dependency_graph()

    print("\nRipple - Unified Dependency Graph")
    print("-" * 45)

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
    print("-" * 45)
    print("Total modules:", len(graph))
    print("Total dependency relationships:", total_edges)
