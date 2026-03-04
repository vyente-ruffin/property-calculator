

def test_root_returns_html(client):
    response = client.get("/")
    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]
    assert "405 Network" in response.text


def test_root_includes_htmx_cdn(client):
    response = client.get("/")
    assert "htmx.org" in response.text


def test_root_includes_daisyui_cdn(client):
    response = client.get("/")
    assert "daisyui" in response.text


def test_static_css_served(client):
    response = client.get("/static/css/theme.css")
    assert response.status_code == 200
