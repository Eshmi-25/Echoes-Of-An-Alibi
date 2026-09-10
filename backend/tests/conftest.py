from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.db.session import engine
from app.seed.seed import main as seed_main


def _reset_db_files() -> None:
    # Ensure SQLite file handles are closed before deleting/recreating DB files.
    engine.dispose()
    for name in ("echoes.db", "echoes.db-wal", "echoes.db-shm"):
        db_file = Path(name)
        if db_file.exists():
            db_file.unlink()


@pytest.fixture
def client() -> TestClient:
    _reset_db_files()
    seed_main()
    with TestClient(app) as test_client:
        yield test_client
    engine.dispose()


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
