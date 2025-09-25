from __future__ import annotations
import importlib


def import_string(path: str):
    """Import a symbol from 'module:Name' or 'module.Name'. Returns the attribute.

    Example: 'wer_tester.mock_provider:MockProvider'
    """
    module_path: str
    attr: str | None = None
    if ':' in path:
        module_path, attr = path.split(':', 1)
    else:
        parts = path.rsplit('.', 1)
        if len(parts) == 2:
            module_path, attr = parts
        else:
            module_path = path
            attr = None
    mod = importlib.import_module(module_path)
    return getattr(mod, attr) if attr else mod
