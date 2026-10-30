
from collections import deque


def analyze_impact(dependency_graph, changed_modules):
    """
    Find all direct and indirect dependents
    of changed modules using BFS.

    Graph direction:
    dependency -> dependent
    """

    impacted_modules = {}
    visited = set(changed_modules)

    queue = deque()

    for module in changed_modules:
        queue.append((module, 0))

    while queue:

        current_module, current_depth = queue.popleft()

        dependents = dependency_graph.get(current_module, [])

        for dependent in dependents:

            if dependent in visited:
                continue

            visited.add(dependent)

            impact_depth = current_depth + 1

            impacted_modules[dependent] = {
                "depth": impact_depth,
                "impact_type": (
                    "direct" if impact_depth == 1
                    else "indirect"
                ),
                "affected_by": current_module,
            }

            queue.append((dependent, impact_depth))

    return impacted_modules


if __name__ == "__main__":

    # Sample dependency graph
    graph = {
        "payment": ["checkout"],
        "checkout": ["main"],
        "main": [],
    }

    changed = ["payment"]

    results = analyze_impact(graph, changed)

    print("\nRipple - Change Impact Analyzer")
    print("-" * 40)

    print("Changed modules:", changed)

    for module, details in results.items():

        print(f"\n{module}")
        print("Impact type:", details["impact_type"])
        print("Impact depth:", details["depth"])
        print("Affected by:", details["affected_by"])

    print("\nTotal impacted modules:", len(results))
