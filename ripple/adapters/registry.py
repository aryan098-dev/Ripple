
from pathlib import Path

from ripple.adapters.base import LanguageAdapter
from ripple.adapters.python_adapter import PythonAdapter
from ripple.adapters.javascript_adapter import JavaScriptAdapter


class LanguageRegistry:
    """Manages available programming language adapters."""

    def __init__(self):
        self.adapters: list[LanguageAdapter] = []

    def register(self, adapter: LanguageAdapter):
        self.adapters.append(adapter)

    def get_adapter(self, file_path: Path):
        for adapter in self.adapters:
            if adapter.supports(file_path):
                return adapter

        return None

    def supported_languages(self) -> list[str]:
        return [
            adapter.__class__.__name__.replace("Adapter", "")
            for adapter in self.adapters
        ]


def create_default_registry() -> LanguageRegistry:
    registry = LanguageRegistry()

    registry.register(PythonAdapter())
    registry.register(JavaScriptAdapter())

    return registry
