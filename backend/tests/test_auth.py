from tests.conftest import auth_headers, get_client


def test_register_and_login():
    client = get_client()
    r = client.post(
        "/api/auth/register",
        json={"username": "alpha", "email": "alpha@example.com", "password": "Secret123!"},
    )
    assert r.status_code == 201

    l = client.post(
        "/api/auth/login",
        json={"username_or_email": "alpha", "password": "Secret123!"},
    )
    assert l.status_code == 200
    assert "access_token" in l.json()


def test_invalid_credentials():
    client = get_client()
    client.post(
        "/api/auth/register",
        json={"username": "beta", "email": "beta@example.com", "password": "Secret123!"},
    )
    l = client.post(
        "/api/auth/login",
        json={"username_or_email": "beta", "password": "WrongPass123"},
    )
    assert l.status_code == 401


def test_protected_route_access():
    client = get_client()
    res = client.get("/api/cases")
    assert res.status_code == 401

    headers = auth_headers(client, "gamma", "gamma@example.com")
    ok = client.get("/api/cases", headers=headers)
    assert ok.status_code == 200
