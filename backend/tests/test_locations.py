from tests.conftest import auth_headers, get_client


def _start(client, headers):
    case_id = client.get("/api/cases", headers=headers).json()[0]["id"]
    inv = client.post("/api/investigations", headers=headers, json={"case_id": case_id}).json()
    return inv["id"]


def test_new_investigation_initialization_and_search_consumes_action_once():
    client = get_client()
    headers = auth_headers(client, "loc1", "loc1@example.com")
    inv_id = _start(client, headers)

    detail = client.get(f"/api/investigations/{inv_id}", headers=headers).json()
    before = detail["actions_remaining"]

    r = client.post(
        f"/api/investigations/{inv_id}/locations/main-gallery/search",
        headers=headers,
    )
    assert r.status_code == 200

    after = client.get(f"/api/investigations/{inv_id}", headers=headers).json()["actions_remaining"]
    assert after == before - 1


def test_location_unlocking():
    client = get_client()
    headers = auth_headers(client, "loc2", "loc2@example.com")
    inv_id = _start(client, headers)

    client.post(f"/api/investigations/{inv_id}/locations/main-gallery/search", headers=headers)
    client.post(f"/api/investigations/{inv_id}/locations/security-office/search", headers=headers)

    locations = client.get(f"/api/investigations/{inv_id}/locations", headers=headers).json()
    slugs = {l["location_slug"]: l["unlocked"] for l in locations}
    assert slugs["restoration-room"] is True
