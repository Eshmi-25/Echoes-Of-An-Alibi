from pathlib import Path

from fastapi.testclient import TestClient

from app.main import app
from app.seed.seed import main as seed_main


def get_client() -> TestClient:
    db_file = Path("echoes.db")
    if db_file.exists():
        db_file.unlink()
    seed_main()
    return TestClient(app)


def auth_headers(client: TestClient, username: str = "detective", email: str = "det@case.io") -> dict[str, str]:
    client.post(
        "/api/auth/register",
        json={"username": username, "email": email, "password": "Secret123!"},
    )
    login = client.post(
        "/api/auth/login",
        json={"username_or_email": username, "password": "Secret123!"},
    )
    token = login.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}
