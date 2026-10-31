import re
import os
import subprocess
from pathlib import Path


def run_tests(test_files, repo_path="."):
    """
    Execute recommended Python and JavaScript test files.

    Python: pytest
    JavaScript: Vitest
    """

    root = Path(repo_path).resolve()

    if not test_files:
        return {
            "success": True,
            "passed": 0,
            "failed": 0,
            "output": "No tests were recommended.",
        }

    python_files = []
    javascript_files = []

    for test_file in test_files:
        path = (root / test_file).resolve()

        # Prevent paths outside the repository
        if not path.is_relative_to(root):
            continue

        if not path.is_file():
            continue

        if path.suffix == ".py":
            python_files.append(str(path))

        elif path.suffix in {".js", ".jsx", ".mjs", ".cjs"}:
            javascript_files.append(str(path))

    if not python_files and not javascript_files:
        return {
            "success": False,
            "passed": 0,
            "failed": 0,
            "output": "No valid supported test files found.",
        }

    total_passed = 0
    total_failed = 0
    outputs = []
    return_codes = []

    # Configure Python module search paths
    env = os.environ.copy()
    python_paths = [str(root)]

    sample_project = root / "sample_project"

    if sample_project.is_dir():
        python_paths.append(str(sample_project))

    existing_pythonpath = env.get("PYTHONPATH", "")

    if existing_pythonpath:
        python_paths.append(existing_pythonpath)

    env["PYTHONPATH"] = os.pathsep.join(python_paths)

    # Run Python tests
    if python_files:
        try:
            result = subprocess.run(
                [
                    "python",
                    "-m",
                    "pytest",
                    "-v",
                    "-q",
                    *python_files,
                ],
                cwd=root,
                env=env,
                capture_output=True,
                text=True,
                timeout=120,
            )

            output = result.stdout + result.stderr
            outputs.append("=== PYTHON TEST RESULTS ===\n" + output)
            return_codes.append(result.returncode)

            for line in output.lower().splitlines():
                parts = line.split()

                for index, word in enumerate(parts):
                    if word == "passed" and index > 0:
                        try:
                            total_passed += int(parts[index - 1])
                        except ValueError:
                            pass

                    elif word == "failed" and index > 0:
                        try:
                            total_failed += int(parts[index - 1])
                        except ValueError:
                            pass

        except subprocess.TimeoutExpired:
            outputs.append("Python tests timed out.")
            return_codes.append(1)

        except OSError as error:
            outputs.append(f"Python test execution error: {error}")
            return_codes.append(1)

    
    # Run JavaScript tests
    if javascript_files:
        try:
            relative_files = [
                str(Path(file).relative_to(root))
                for file in javascript_files
            ]

            result = subprocess.run(
                [
                    "npx",
                    "--no-install",
                    "vitest",
                    "run",
                    *relative_files,
                ],
                cwd=root,
                env=env,
                capture_output=True,
                text=True,
                timeout=120,
            )

            output = result.stdout + result.stderr
            outputs.append("=== JAVASCRIPT TEST RESULTS ===\n" + output)
            return_codes.append(result.returncode)

            # Remove terminal color codes before parsing
            clean_output = re.sub(r"\x1b\[[0-9;]*m", "", output)

            passed_match = re.search(
                r"Tests\s+(\d+)\s+passed", clean_output
            )

            failed_match = re.search(
                r"Tests\s+(\d+)\s+failed", clean_output
            )

            if passed_match:
                total_passed += int(passed_match.group(1))

            if failed_match:
                total_failed += int(failed_match.group(1))

        except subprocess.TimeoutExpired:
            outputs.append("JavaScript tests timed out.")
            return_codes.append(1)

        except OSError as error:
            outputs.append(f"JavaScript test execution error: {error}")
            return_codes.append(1)


    return {
        "success": all(code == 0 for code in return_codes),
        "passed": total_passed,
        "failed": total_failed,
        "return_code": 0 if all(code == 0 for code in return_codes) else 1,
        "output": "\n\n".join(outputs),
    }


if __name__ == "__main__":
    sample_tests = [
        "sample_project/tests/test_checkout.py",
        "sample_project/app.test.js",
    ]

    results = run_tests(sample_tests)

    print("\nRipple - Automated Test Runner")
    print("-" * 40)
    print(results["output"])

    print("\nCombined Test Summary")
    print("-" * 40)
    print("Passed:", results["passed"])
    print("Failed:", results["failed"])
    print("Execution successful:", results["success"])
