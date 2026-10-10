import pytest
from config import settings
from security import workspace_path


def test_traversal_is_blocked(tmp_path, monkeypatch):
    monkeypatch.setattr(settings, "orbit_workspace", str(tmp_path))
    with pytest.raises(ValueError):
        workspace_path("../../outside.txt")


def test_nested_workspace_path_is_allowed(tmp_path, monkeypatch):
    monkeypatch.setattr(settings, "orbit_workspace", str(tmp_path))
    assert workspace_path("project/readme.txt") == (tmp_path / "project" / "readme.txt").resolve()
