
import subprocess
from pathlib import Path


def get_changed_files(repo_path="."):
    """
    Detect changed files in a Git repository.

    Returns a list of files with their change types.
    """

    try:
        result = subprocess.run(
            [
                "git",
                "-C",
                str(Path(repo_path).resolve()),
                "status",
                "--short",
                "--untracked-files=all",
            ],
            capture_output=True,
            text=True,
            check=True,
        )

    except subprocess.CalledProcessError:
        raise RuntimeError("Unable to read Git repository status.")

    changed_files = []

    for line in result.stdout.splitlines():

        if len(line) < 4:
            continue

        status = line[:2]
        filename = line[3:]

        if status == "??" or "A" in status:
            change_type = "added"

        elif "D" in status:
            change_type = "deleted"

        elif "R" in status:
            change_type = "renamed"

        else:
            change_type = "modified"

        changed_files.append({
            "file": filename,
            "status": status,
            "change_type": change_type,
        })

    return changed_files


if __name__ == "__main__":

    changes = get_changed_files()

    if not changes:
        print("No changes detected.")

    else:
        print("\nRipple - Git Change Detector")
        print("-" * 35)

        for change in changes:
            print(
                f"{change['change_type'].upper():10}"
                f" {change['file']}"
            )

        print(f"\nTotal changed files: {len(changes)}")
