from fastapi.testclient import TestClient

from roster_balance.main import app

client = TestClient(app)


def test_team_crud_is_exposed_in_openapi_and_http() -> None:
    schema = client.get("/openapi.json").json()
    assert "/teams" in schema["paths"]
    assert "/teams/{team_id}" in schema["paths"]

    created = client.post(
        "/teams", json={"name": "Platform", "description": "Core services"}
    )
    assert created.status_code == 201
    team = created.json()
    assert team["name"] == "Platform"

    fetched = client.get(f"/teams/{team['id']}")
    assert fetched.status_code == 200
    assert fetched.json()["id"] == team["id"]

    updated = client.patch(f"/teams/{team['id']}", json={"active": False})
    assert updated.status_code == 200
    assert updated.json()["active"] is False

    cleared = client.patch(f"/teams/{team['id']}", json={"description": None})
    assert cleared.status_code == 200
    assert cleared.json()["description"] is None

    deleted = client.delete(f"/teams/{team['id']}")
    assert deleted.status_code == 204
    assert client.get(f"/teams/{team['id']}").status_code == 404


def test_duplicate_team_names_are_rejected() -> None:
    first = client.post("/teams", json={"name": "Unique team"})
    assert first.status_code == 201
    duplicate = client.post("/teams", json={"name": "UNIQUE TEAM"})
    assert duplicate.status_code == 409
