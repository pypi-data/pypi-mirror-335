from .http_client import SimpleHttpClient


def test_get():
    client = SimpleHttpClient()
    res = client.get("https://one.one.one.one/")
    assert res.status_code == 200
