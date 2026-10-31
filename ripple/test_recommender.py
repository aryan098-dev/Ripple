
import ast
import re
from pathlib import Path


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


SUPPORTED_EXTENSIONS = {
    ".py", ".js", ".jsx", ".mjs", ".cjs"
}


def discover_test_files(repo_path="."):
    """Discover Python and JavaScript test files."""

    root = Path(repo_path).resolve()
    test_files = []

    for path in root.rglob("*"):

        if not path.is_file():
            continue

        relative_parts = path.relative_to(root).parts

        if any(part in IGNORED_DIRS for part in relative_parts):
            continue

        if "ripple" in relative_parts:
            continue

        if path.suffix.lower() not in SUPPORTED_EXTENSIONS:
            continue

        name = path.name.lower()

        is_python_test = (
            name.startswith("test_")
            or name.endswith("_test.py")
        ) and path.suffix.lower() == ".py"

        is_javascript_test = (
            ".test." in name
            or ".spec." in name
        ) and path.suffix.lower() in {
            ".js", ".jsx", ".mjs", ".cjs"
        }

        is_inside_tests_directory = (
            "tests" in relative_parts
            or "__tests__" in relative_parts
        )

        if (
            is_python_test
            or is_javascript_test
            or is_inside_tests_directory
        ):
            test_files.append(path)

    return sorted(set(test_files))


def get_module_name(module_id):
    """Extract the source filename stem from a module identifier."""

    module_id = module_id.lower()

    if ":" in module_id:
        module_id = module_id.split(":", 1)[1]

    return module_id.split(".")[-1]


def get_test_target(test_file):
    """Extract the production module targeted by a test filename."""

    name = test_file.name.lower()

    if test_file.suffix.lower() == ".py":

        test_name = test_file.stem

        if test_name.startswith("test_"):
            return test_name[5:]

        if test_name.endswith("_test"):
            return test_name[:-5]

    else:
        for marker in (".test.", ".spec."):

            if marker in name:
                return name.split(marker, 1)[0]

    return None


def extract_python_test_imports(test_file):
    """Extract imported module names from a Python test."""

    try:
        source = test_file.read_text(encoding="utf-8")
        tree = ast.parse(source)
    except (OSError, SyntaxError, UnicodeDecodeError):
        return set()

    imports = set()

    for node in ast.walk(tree):

        if isinstance(node, ast.Import):

            for alias in node.names:
                imports.add(alias.name.lower())

        elif isinstance(node, ast.ImportFrom):

            if node.module:
                imports.add(node.module.lower())

    return imports


def extract_javascript_test_imports(test_file):
    """Extract module paths from JavaScript test imports."""

    try:
        source = test_file.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError):
        return set()

    imports = set()

    patterns = [
        r'import\s+(?:[\s\S]*?\s+from\s+)?["\']([^"\']+)["\']',
        r'require\(\s*["\']([^"\']+)["\']\s*\)',
        r'import\(\s*["\']([^"\']+)["\']\s*\)',
    ]

    for pattern in patterns:

        for match in re.finditer(pattern, source):
            imports.add(match.group(1).lower())

    return imports


def normalize_module_path(module_id):
    """Convert a module identifier into a normalized path."""

    module_id = module_id.lower()

    if ":" in module_id:
        module_id = module_id.split(":", 1)[1]

    return module_id.replace(".", "/")


def resolve_test_import(import_name, test_file, root):
    """Resolve an imported module to a repository-relative path."""

    import_name = import_name.strip().lower()

    if not import_name:
        return None

    # Resolve relative JavaScript imports.
    if import_name.startswith("."):

        resolved = (
            test_file.parent / import_name
        ).resolve()

        try:
            return resolved.relative_to(root).with_suffix("").as_posix()
        except ValueError:
            return None

    # Normalize Python module imports.
    return import_name.replace(".", "/")


def is_import_match(import_path, module_id):
    """Check whether a test import matches an affected module."""

    module_path = normalize_module_path(module_id)

    import_path = import_path.removesuffix(".js")
    import_path = import_path.removesuffix(".jsx")
    import_path = import_path.removesuffix(".mjs")
    import_path = import_path.removesuffix(".cjs")

    return (
        import_path == module_path
        or module_path.endswith("/" + import_path)
    )


def recommend_tests(impacted_modules, test_files, repo_path="."):
    """
    Recommend tests using dependency imports and filename matching.

    Import-based matches receive higher priority than filename matches.
    """

    root = Path(repo_path).resolve()
    recommendations = []

    for test_file in test_files:

        try:
            relative_path = test_file.relative_to(root)
        except ValueError:
            continue

        if test_file.suffix.lower() == ".py":
            test_imports = extract_python_test_imports(test_file)
        else:
            test_imports = extract_javascript_test_imports(test_file)

        resolved_imports = {
            resolve_test_import(name, test_file, root)
            for name in test_imports
        }

        resolved_imports.discard(None)

        filename_target = get_test_target(test_file)

        imported_matches = []
        filename_matches = []

        for module, details in impacted_modules.items():

            module_lower = module.lower()

            parts = module_lower.replace(":", ".").split(".")

            # Never recommend a test as a production module.
            if (
                "tests" in parts
                or "__tests__" in parts
                or module_lower.endswith(".test")
                or module_lower.endswith(".spec")
                or get_module_name(module).startswith("test_")
            ):
                continue

            # Strong match: the test imports an affected module.
            if any(
                is_import_match(import_path, module)
                for import_path in resolved_imports
            ):
                imported_matches.append(module)

            # Fallback: test filename matches an affected module.
            elif (
                filename_target
                and get_module_name(module) == filename_target
            ):
                filename_matches.append(module)

        matched_modules = sorted(
            set(imported_matches + filename_matches)
        )

        if not matched_modules:
            continue

        if imported_matches:

            priority = "high"

            reason = (
                "Test directly imports one or more "
                "changed or impacted production modules."
            )

        else:

            priority = "medium"

            reason = (
                "Test filename matches an affected "
                "production module."
            )

        recommendations.append({
            "test_file": str(relative_path),
            "matched_modules": matched_modules,
            "priority": priority,
            "reason": reason,
            "match_type": (
                "import"
                if imported_matches
                else "filename"
            ),
        })

    priority_order = {
        "high": 0,
        "medium": 1,
    }

    recommendations.sort(
        key=lambda item: (
            priority_order[item["priority"]],
            item["test_file"],
        )
    )

    return recommendations


if __name__ == "__main__":

    tests = discover_test_files()

    print("\nRipple - Intelligent Test Recommender")
    print("-" * 45)

    print("Test files discovered:", len(tests))

    for test_file in tests:
        print(test_file)
