
import re
from pathlib import Path

from ripple.adapters.base import LanguageAdapter


class JavaScriptAdapter(LanguageAdapter):
    """Language adapter for JavaScript projects."""

    SUPPORTED_EXTENSIONS = {".js", ".jsx", ".mjs", ".cjs"}

    def supports(self, file_path: Path) -> bool:
        return file_path.suffix.lower() in self.SUPPORTED_EXTENSIONS

    def extract_imports(
        self,
        file_path: Path,
        root_path: Path
    ) -> list[str]:
        try:
            source = file_path.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            return []

        patterns = [
            r"""import\s+(?:.*?\s+from\s+)?["']([^"']+)["']""",
            r"""export\s+.*?\s+from\s+["']([^"']+)["']""",
            r"""require\(\s*["']([^"']+)["']\s*\)""",
            r"""import\(\s*["']([^"']+)["']\s*\)""",
        ]

        imports = set()

        for pattern in patterns:
            for match in re.finditer(pattern, source):
                imports.add(match.group(1))

        return sorted(imports)

    def extract_symbols(self, file_path: Path) -> dict:
        try:
            source = file_path.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            return {}

        function_pattern = (
            r"(?:async\s+)?function\s+([A-Za-z_$][\w$]*)"
        )

        class_pattern = (
            r"class\s+([A-Za-z_$][\w$]*)"
        )

        functions = re.findall(function_pattern, source)
        classes = re.findall(class_pattern, source)

        return {
            "functions": sorted(set(functions)),
            "classes": sorted(set(classes)),
        }

    def discover_tests(self, root_path: Path) -> list[Path]:
        ignored_dirs = {
            ".git",
            "node_modules",
            "dist",
            "build",
            ".next",
        }

        test_files = []

        for path in root_path.rglob("*"):
            if not path.is_file():
                continue

            relative_parts = path.relative_to(root_path).parts

            if any(part in ignored_dirs for part in relative_parts):
                continue

            if path.suffix.lower() not in self.SUPPORTED_EXTENSIONS:
                continue

            if (
                path.name.endswith(".test.js")
                or path.name.endswith(".spec.js")
                or path.name.endswith(".test.jsx")
                or path.name.endswith(".spec.jsx")
                or "tests" in relative_parts
            ):
                test_files.append(path)

        return sorted(set(test_files))
