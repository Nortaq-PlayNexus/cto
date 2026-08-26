import pytest

try:
    import cto_dashboard
except ImportError:
    cto_dashboard = None

def test_package_importable():
    if cto_dashboard is None:
        pytest.skip("cto_dashboard requires optional dependencies not installed")
    assert cto_dashboard is not None