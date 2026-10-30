
from pathlib import Path


def discover_test_files(repo_path="."):
    """
    Discover Python test files in a repository.
    """

    root = Path(repo_path).resolve()

    ignored_dirs = {
        ".git",
        ".venv",
        "venv",
        "__pycache__",
        "site-packages",
    }

    test_files = []

    for path in root.rglob("*.py"):
        if path.resolve() == Path(__file__).resolve():
            continue

        if any(part in ignored_dirs for part in path.parts):
            continue

        if (
            path.name.startswith("test_")
            or path.name.endswith("_test.py")
            or "tests" in path.parts
        ):
            test_files.append(path)

    return sorted(test_files)



def recommend_tests(impacted_modules, test_files, repo_path="."):
    """
    Recommend tests for impacted production modules.

    Matches test filenames with production module names.
    Test modules are excluded from impact targets.
    """

    root = Path(repo_path).resolve()

    recommendations = []

    for test_file in test_files:

        relative_path = test_file.relative_to(root)
        test_name = test_file.stem.lower()

        # Normalize test filename
        if test_name.startswith("test_"):
            target_name = test_name[5:]

        elif test_name.endswith("_test"):
            target_name = test_name[:-5]

        else:
            target_name = test_name

        matched_modules = []

        for module, details in impacted_modules.items():

            parts = module.lower().split(".")
            module_name = parts[-1]

            # Ignore test modules and test directories
            if (
                "tests" in parts
                or module_name.startswith("test_")
                or module_name.endswith("_test")
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

    sample_impact = {
    "sample_project.checkout": {
        "depth": 1,
        "impact_type": "direct",
    },
    "sample_project.main": {
        "depth": 2,
        "impact_type": "indirect",
    },
    "sample_project.tests.test_checkout": {
        "depth": 1,
        "impact_type": "direct",
    },
}

    tests = discover_test_files()

    results = recommend_tests(
        sample_impact,
        tests,
    )

    print("\nRipple - Test Recommendation Engine")
    print("-" * 45)

    print("Test files discovered:", len(tests))

    for recommendation in results:

        print("\nRecommended test:")
        print("File:", recommendation["test_file"])
        print("Affected modules:", recommendation["matched_modules"])
        print("Reason:", recommendation["reason"])

    print("\nTotal recommendations:", len(results))
