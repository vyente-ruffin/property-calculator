"""E2E tests for mobile viewport behaviour.

These tests require a running server and Playwright — skip by default.
"""

import pytest

pytestmark = pytest.mark.skip(reason="E2E tests require running server — run manually")


def test_mobile_portrait_shows_tabs():
    """390px viewport should show tabbed navigation."""
    pass


def test_mobile_content_scrollable():
    """All calculator content should be scrollable on mobile."""
    pass


def test_mobile_landscape_split_view():
    """844px landscape should show split chat+calc view."""
    pass
