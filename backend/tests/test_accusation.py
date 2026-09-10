from tests.conftest import auth_headers


def _start(client, headers):
    case_id = client.get("/api/cases", headers=headers).json()[0]["id"]
    inv = client.post("/api/investigations", headers=headers, json={"case_id": case_id}).json()
    return inv["id"]


def _collect_core_clues(client, headers, inv_id):
    client.post(f"/api/investigations/{inv_id}/locations/main-gallery/search", headers=headers)
    client.post(f"/api/investigations/{inv_id}/locations/security-office/search", headers=headers)
    client.post(f"/api/investigations/{inv_id}/locations/restoration-room/search", headers=headers)
    client.post(f"/api/investigations/{inv_id}/locations/loading-dock/search", headers=headers)


def test_correct_accusation(client):
    headers = auth_headers(client, "acc1", "acc1@example.com")
    inv_id = _start(client, headers)
    _collect_core_clues(client, headers, inv_id)

    res = client.post(
        f"/api/investigations/{inv_id}/accusations",
        headers=headers,
        json={
            "attacker_slug": "celeste-vale",
            "thief_slug": "marina-crowe",
            "motive": "protect family debt secrets and force insurance leverage",
            "supporting_clues": ["restoration-key-imprint", "dock-delivery-log"],
            "explanation": "The timeline and transport log place Marina at the theft route and Celeste at the attack point.",
        },
    )
    assert res.status_code == 200
    assert res.json()["score"] >= 70


def test_wrong_accusation(client):
    headers = auth_headers(client, "acc2", "acc2@example.com")
    inv_id = _start(client, headers)
    _collect_core_clues(client, headers, inv_id)

    res = client.post(
        f"/api/investigations/{inv_id}/accusations",
        headers=headers,
        json={
            "attacker_slug": "jonah-pryce",
            "thief_slug": "darius-holt",
            "motive": "career jealousy",
            "supporting_clues": ["restoration-key-imprint", "dock-delivery-log"],
            "explanation": "A weak claim.",
        },
    )
    assert res.status_code == 200
    assert res.json()["score"] < 60
