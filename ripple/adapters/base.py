
from abc import ABC, abstractmethod
from pathlib import Path


class LanguageAdapter(ABC):
    """
    Base interface for all programming language adapters.
    Every language adapter must implement these methods.
    """

    @abstractmethod
    def supports(self, file_path: Path) -> bool:
        """Check whether this adapter supports the given file."""
        pass

    @abstractmethod
    def extract_imports(self, file_path: Path, root_path: Path) -> list[str]:
        """Extract dependencies imported by the given file."""
        pass

    @abstractmethod
    def extract_symbols(self, file_path: Path) -> dict:
        """Extract functions, classes, and other relevant symbols."""
        pass

    @abstractmethod
    def discover_tests(self, root_path: Path) -> list[Path]:
        """Find test files belonging to this language."""
        pass
