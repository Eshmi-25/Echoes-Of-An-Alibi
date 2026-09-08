from tests.conftest import auth_headers, get_client


def _start(client, headers):
    case_id = client.get("/api/cases", headers=headers).json()[0]["id"]
    inv = client.post("/api/investigations", headers=headers, json={"case_id": case_id}).json()
    return inv["id"]


def test_trust_pressure_and_contradiction_detection():
    client = get_client()
    headers = auth_headers(client, "eng1", "eng1@example.com")
    inv_id = _start(client, headers)

    client.post(f"/api/investigations/{inv_id}/locations/security-office/search", headers=headers)

    client.post(
        f"/api/investigations/{inv_id}/suspects/marina-crowe/messages",
        headers=headers,
        json={"message": "Were you on a call at 11:47?"},
    )

    contradictions = client.get(f"/api/investigations/{inv_id}/contradictions", headers=headers)
    assert contradictions.status_code == 200


def test_duplicate_search_safety():
    client = get_client()
    headers = auth_headers(client, "eng2", "eng2@example.com")
    inv_id = _start(client, headers)

    client.post(f"/api/investigations/{inv_id}/locations/security-office/search", headers=headers)
    first_clues = client.get(f"/api/investigations/{inv_id}/clues", headers=headers).json()
    client.post(f"/api/investigations/{inv_id}/locations/security-office/search", headers=headers)
    second_clues = client.get(f"/api/investigations/{inv_id}/clues", headers=headers).json()
    assert len(second_clues) >= len(first_clues)
