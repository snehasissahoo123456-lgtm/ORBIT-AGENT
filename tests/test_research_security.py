import pytest
from research import _assert_public_https


def test_browser_reader_rejects_localhost():
    with pytest.raises(ValueError):
        _assert_public_https("https://localhost/admin")


def test_browser_reader_rejects_plain_http():
    with pytest.raises(ValueError):
        _assert_public_https("http://example.com")


def test_browser_reader_rejects_loopback_ip():
    with pytest.raises(ValueError):
        _assert_public_https("https://127.0.0.1/")
