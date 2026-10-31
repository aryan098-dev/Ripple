
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


def discover_test_files(repo_path="."):
    """Discover Python and JavaScript test files."""

    root = Path(repo_path).resolve()
    test_files = []

    supported_extensions = {
        ".py", ".js", ".jsx", ".mjs", ".cjs"
    }

    for path in root.rglob("*"):

        if not path.is_file():
            continue

        relative_parts = path.relative_to(root).parts

        if any(part in IGNORED_DIRS for part in relative_parts):
            continue

        if "ripple" in relative_parts:
            continue

        if path.suffix.lower() not in supported_extensions:
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

    # Remove language prefix from identifiers such as
    # javascript:sample_project.app
    if ":" in module_id:
        module_id = module_id.split(":", 1)[1]

    return module_id.split(".")[-1]


def get_test_target(test_file):
    """Extract the production module name targeted by a test."""

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


def recommend_tests(impacted_modules, test_files, repo_path="."):
    """
    Recommend tests matching changed or impacted modules.

    Supports Python and JavaScript test naming conventions.
    """

    root = Path(repo_path).resolve()
    recommendations = []

    for test_file in test_files:

        relative_path = test_file.relative_to(root)
        target_name = get_test_target(test_file)

        if not target_name:
            continue

        matched_modules = []

        for module, details in impacted_modules.items():

            module_name = get_module_name(module)

            parts = module.lower().replace(":", ".").split(".")

            if (
                "tests" in parts
                or "__tests__" in parts
                or module_name.startswith("test_")
                or ".test." in module
                or ".spec." in module
            ):
                continue

            if module_name == target_name:
                matched_modules.append(module)

        if matched_modules:

            recommendations.append({
                "test_file": str(relative_path),
                "matched_modules": sorted(matched_modules),
                "reason": (
                    "Test filename matches an impacted "
                    "production module"
                ),
            })

    return recommendations


if __name__ == "__main__":

    tests = discover_test_files()

    print("\nRipple - Multi-Language Test Recommender")
    print("-" * 45)

    print("Test files discovered:", len(tests))

    for test_file in tests:
        print(test_file)

