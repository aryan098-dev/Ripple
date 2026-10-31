
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

    print("\n" + "=" * 50)
    print("          RIPPLE INTELLIGENCE ENGINE")
    print("=" * 50)

    # Step 1: Detect changed files
    print("\n[1] Detecting changed files...")

    changes = get_changed_files(root)

    for change in changes:
        print(
            f"  {change['change_type'].upper():10}"
            f" {change['file']}"
        )

    if not changes:
        print("  No changes detected.")
        return

    # Step 2: Analyze changed files
    print("\n[2] Analyzing changed source files...")

    changed_modules = []
    analysis_results = []

    for change in changes:
        file_path = root / change["file"]
        adapter = registry.get_adapter(file_path)

        if adapter is None:
            continue

        module_name = get_file_module_id(
            file_path,
            root,
            adapter,
        )

        changed_modules.append(module_name)

        if not file_path.is_file():
            print(f"  Deleted or unavailable: {change['file']}")
            continue

        symbols = adapter.extract_symbols(file_path)

        if not symbols:
            print(f"  Analysis unavailable: {change['file']}")
            continue

        analysis_results.append({
            "file": change["file"],
            "language": adapter.__class__.__name__,
            "symbols": symbols,
        })

        print(
            f"  Analyzed: {change['file']} "
            f"({adapter.__class__.__name__})"
        )

    changed_modules = sorted(set(changed_modules))

    # Step 3: Build dependency graph
    print("\n[3] Building unified dependency graph...")

    graph = build_dependency_graph(root)

    print("  Modules discovered:", len(graph))
    print(
        "  Dependency relationships:",
        sum(len(dependents) for dependents in graph.values())
    )

    # Step 4: Analyze impact
    print("\n[4] Calculating change impact...")

    impacted = analyze_impact(graph, changed_modules)

    if impacted:
        for module, details in sorted(impacted.items()):
            print(
                f"  {module} | "
                f"{details['impact_type']} | "
                f"Level {details['depth']}"
            )
    else:
        print("  No additional impacted modules detected.")

    # Step 5: Recommend tests
    print("\n[5] Generating test recommendations...")

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

    for recommendation in recommendations:
        print("\n  Recommended:", recommendation["test_file"])
        print("  Matches:", recommendation["matched_modules"])
        print("  Reason:", recommendation["reason"])

    if not recommendations:
        print("  No matching tests found.")

    # Step 6: Execute multi-language tests
    print("\n[6] Executing recommended tests...")

    recommended_files = [
        item["test_file"]
        for item in recommendations
    ]

    test_results = run_tests(recommended_files, root)

    print("\nMulti-language Test Results")
    print("-" * 35)
    print("Passed:", test_results["passed"])
    print("Failed:", test_results["failed"])
    print("Execution successful:", test_results["success"])

    if test_results["output"]:
        print("\nTest output:")
        print(test_results["output"])

    # Final report
    print("\n" + "=" * 50)
    print("             RIPPLE REPORT")
    print("=" * 50)

    print("Changed source modules:", len(changed_modules))
    print("Successfully analyzed files:", len(analysis_results))
    print("Dependency relationships:", sum(
        len(dependents) for dependents in graph.values()
    ))
    print("Impacted modules:", len(impacted))
    print("Test files discovered:", len(test_files))
    print("Test recommendations:", len(recommendations))
    print("Tests passed:", test_results["passed"])
    print("Tests failed:", test_results["failed"])
    print("Test execution successful:", test_results["success"])

    print("\nRipple analysis completed.")
    print("=" * 50)


if __name__ == "__main__":
    run_ripple()
