import pytest
from config import settings
from developer_engine import _safe_file
from process_tools import validate_command


def test_terminal_command_allowlist():
    assert validate_command("python --version")[0].lower().startswith("python")


def test_shell_composition_is_blocked():
    with pytest.raises(ValueError):
        validate_command("python --version && whoami")


def test_unapproved_executable_is_blocked():
    with pytest.raises(ValueError):
        validate_command("powershell -Command whoami")


def test_developer_path_cannot_escape_workspace(tmp_path, monkeypatch):
    monkeypatch.setattr(settings, "orbit_workspace", str(tmp_path))
    with pytest.raises(ValueError):
        _safe_file("../../outside.py")


def test_developer_path_blocks_secret_files(tmp_path, monkeypatch):
    monkeypatch.setattr(settings, "orbit_workspace", str(tmp_path))
    with pytest.raises(ValueError):
        _safe_file(".env")
