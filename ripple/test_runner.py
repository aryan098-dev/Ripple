
import os
import subprocess
from pathlib import Path


def run_tests(test_files, repo_path="."):
    """
    Execute recommended test files using pytest.

    Returns execution status, test counts and output.
    """

    root = Path(repo_path).resolve()

    if not test_files:
        return {
            "success": True,
            "passed": 0,
            "failed": 0,
            "output": "No tests were recommended.",
        }

    valid_files = []

    for test_file in test_files:

        path = (root / test_file).resolve()

        # Prevent paths outside the repository
        if not path.is_relative_to(root):
            continue

        if path.is_file():
            valid_files.append(str(path))

    if not valid_files:
        return {
            "success": False,
            "passed": 0,
            "failed": 0,
            "output": "No valid test files found.",
        }

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

    try:

        result = subprocess.run(
            [
                "python",
                "-m",
                "pytest",
                "-v",
                "-q",
                *valid_files,
            ],
            cwd=root,
            env=env,
            capture_output=True,
            text=True,
            timeout=120,
        )

        output = result.stdout + result.stderr

        # Extract exact test counts from pytest output
        summary = output.lower()

        passed = 0
        failed = 0

        for line in summary.splitlines():

            if " passed" in line:
                try:
                    passed = max(
                        passed,
                        int(line.split(" passed")[0].split()[-1])
                    )
                except (ValueError, IndexError):
                    pass

            if " failed" in line:
                try:
                    failed = max(
                        failed,
                        int(line.split(" failed")[0].split()[-1])
                    )
                except (ValueError, IndexError):
                    pass

        return {
            "success": result.returncode == 0,
            "passed": passed,
            "failed": failed,
            "return_code": result.returncode,
            "output": output,
        }

    except subprocess.TimeoutExpired:

        return {
            "success": False,
            "passed": 0,
            "failed": 0,
            "output": "Test execution timed out.",
        }

    except OSError as error:

        return {
            "success": False,
            "passed": 0,
            "failed": 0,
            "output": str(error),
        }


if __name__ == "__main__":

    sample_tests = [
        "sample_project/tests/test_checkout.py"
    ]

    results = run_tests(sample_tests)

    print("\nRipple - Automated Test Runner")
    print("-" * 40)

    print(results["output"])

    print("\nTest Summary")
    print("-" * 40)

    print("Passed:", results["passed"])
    print("Failed:", results["failed"])
    print("Execution successful:", results["success"])
