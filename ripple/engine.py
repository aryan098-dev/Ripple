
from pathlib import Path

from ripple.git_diff import get_changed_files
from ripple.ast_analyzer import analyze_python_file
from ripple.dependency_graph import (
    build_dependency_graph,
    get_module_name,
)
from ripple.impact_analyzer import analyze_impact
from ripple.test_recommender import (
    discover_test_files,
    recommend_tests,
)
from ripple.test_runner import run_tests


def run_ripple(repo_path="."):
    """Run the complete Ripple analysis pipeline."""

    root = Path(repo_path).resolve()

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

    # Step 2: Analyze changed Python files
    print("\n[2] Analyzing changed Python files...")

    changed_modules = []
    analysis_results = []

    for change in changes:

        if not change["file"].endswith(".py"):
            continue

        file_path = root / change["file"]

        if not file_path.is_file():
            print(f"  Skipping unavailable file: {change['file']}")
            continue

        module_name = get_module_name(file_path, root)

        changed_modules.append(module_name)

        result = analyze_python_file(file_path)

        if "error" in result:
            print(f"  Analysis error: {change['file']}")
        else:
            analysis_results.append(result)
            print(f"  Analyzed: {change['file']}")

    changed_modules = sorted(set(changed_modules))

    # Step 3: Build dependency graph
    print("\n[3] Building dependency graph...")

    graph = build_dependency_graph(root)

    print("  Modules discovered:", len(graph))

    # Step 4: Analyze change impact
    print("\n[4] Calculating change impact...")

    impacted = analyze_impact(
        graph,
        changed_modules,
    )

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

    # Include changed modules and their dependents
    # so tests can also be suggested for directly changed code.
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


    # Step 6: Execute recommended tests
    print("\n[6] Executing recommended tests...")

    recommended_files = [
        item["test_file"]
        for item in recommendations
    ]

    test_results = run_tests(
        recommended_files,
        root,
    )

    print("\nTest Execution Results")
    print("-" * 35)
    print("Passed:", test_results["passed"])
    print("Failed:", test_results["failed"])
    print("Execution successful:", test_results["success"])

    if test_results["output"]:
        print("\nTest output:")
        print(test_results["output"])


    # Final summary
    print("\n" + "=" * 50)
    print("             RIPPLE REPORT")
    print("=" * 50)

    print("Changed Python modules:", len(changed_modules))
    print("Successfully analyzed files:", len(analysis_results))
    print("Dependency relationships:", sum(
        len(dependents) for dependents in graph.values()
    ))
    print("Impacted modules:", len(impacted))
    print("Test files discovered:", len(test_files))
    print("Test recommendations:", len(recommendations))

    print("\nRipple analysis completed.")
    print("=" * 50)
    print("Tests passed:", test_results["passed"])
    print("Tests failed:", test_results["failed"])


if __name__ == "__main__":
    run_ripple()
