
from pathlib import Path

from ripple.git_diff import get_changed_files
from ripple.adapters.registry import create_default_registry
from ripple.dependency_graph import (
    build_dependency_graph,
    get_file_module_id,
)
from ripple.impact_analyzer import analyze_impact
from ripple.test_recommender import (
    discover_test_files,
    recommend_tests,
)
from ripple.test_runner import run_tests


def run_ripple(repo_path="."):
    """Run Ripple's multi-language analysis pipeline."""

    root = Path(repo_path).resolve()
    registry = create_default_registry()

    # Step 1: Detect changes
    changes = get_changed_files(root)

    changed_modules = []
    analysis_results = []

    for change in changes:
        file_path = root / change["file"]
        adapter = registry.get_adapter(file_path)

        if adapter is None:
            continue

        module_name = get_file_module_id(
            file_path, root, adapter
        )
        changed_modules.append(module_name)

        if not file_path.is_file():
            continue

        symbols = adapter.extract_symbols(file_path)

        if symbols:
            analysis_results.append({
                "file": change["file"],
                "language": adapter.__class__.__name__,
                "symbols": symbols,
            })

    changed_modules = sorted(set(changed_modules))

    # Step 2: Build dependency graph
    graph = build_dependency_graph(root)

    # Step 3: Analyze impact
    impacted = analyze_impact(graph, changed_modules)

    # Step 4: Discover and recommend tests
    test_files = discover_test_files(root)

    analysis_targets = {
        module: {
            "depth": 0,
            "impact_type": "changed",
        }
        for module in changed_modules
    }

    analysis_targets.update(impacted)

    recommendations = recommend_tests(
        analysis_targets,
        test_files,
        root,
    )

    # Step 5: Execute recommended tests
    recommended_files = [
        item["test_file"]
        for item in recommendations
    ]

    test_results = run_tests(recommended_files, root)

    # Step 6: Return structured results
    return {
        "changed_files": changes,
        "changed_modules": changed_modules,
        "analysis_results": analysis_results,
        "dependency_graph": graph,
        "impacted_modules": impacted,
        "test_files_discovered": [
            str(path.relative_to(root))
            for path in test_files
        ],
        "recommendations": recommendations,
        "test_results": test_results,
        "summary": {
            "changed_modules": len(changed_modules),
            "analyzed_files": len(analysis_results),
            "dependency_relationships": sum(
                len(dependents)
                for dependents in graph.values()
            ),
            "impacted_modules": len(impacted),
            "tests_discovered": len(test_files),
            "tests_recommended": len(recommendations),
            "tests_passed": test_results["passed"],
            "tests_failed": test_results["failed"],
            "execution_successful": test_results["success"],
        },
    }


if __name__ == "__main__":
    import json

    results = run_ripple()

    print(json.dumps(results["summary"], indent=4))
