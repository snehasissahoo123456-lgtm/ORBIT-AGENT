from pathlib import Path
from config import settings


def workspace_path(relative: str) -> Path:
    if not relative or not relative.strip():
        raise ValueError("A relative workspace path is required.")
    root = settings.workspace.resolve()
    target = (root / relative).resolve()
    if target != root and root not in target.parents:
        raise ValueError("Path is outside ORBIT's workspace.")
    return target
