from tests.conftest import auth_headers


def _start(client, headers):
    case_id = client.get("/api/cases", headers=headers).json()[0]["id"]
    inv = client.post("/api/investigations", headers=headers, json={"case_id": case_id}).json()
    return inv["id"]


def test_investigation_ownership(client):
    h1 = auth_headers(client, "own1", "own1@example.com")
    h2 = auth_headers(client, "own2", "own2@example.com")

    inv_id = _start(client, h1)
    foreign = client.get(f"/api/investigations/{inv_id}", headers=h2)
    assert foreign.status_code == 403


def test_hidden_fields_absent_from_case_response(client):
    headers = auth_headers(client, "own3", "own3@example.com")
    case_id = client.get("/api/cases", headers=headers).json()[0]["id"]
    case = client.get(f"/api/cases/{case_id}", headers=headers).json()
    assert "canonical_answer" not in case
    assert "hidden_motive" not in case
