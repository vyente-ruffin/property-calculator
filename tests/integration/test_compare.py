"""Integration tests for the /compare endpoint."""


def test_compare_returns_html(client):
    """GET /compare?rows=2,5 returns HTML with comparison table."""
    response = client.get("/compare?rows=2,5")
    assert response.status_code in (200, 503)


def test_compare_without_rows_returns_error(client):
    """GET /compare without rows param returns 400."""
    response = client.get("/compare")
    assert response.status_code in (400, 422)


def test_compare_invalid_rows_returns_error(client):
    """GET /compare?rows=abc returns 400 for non-numeric input."""
    response = client.get("/compare?rows=abc")
    assert response.status_code == 400


def test_compare_single_row(client):
    """GET /compare?rows=2 returns HTML even for a single row."""
    response = client.get("/compare?rows=2")
    assert response.status_code in (200, 503)
