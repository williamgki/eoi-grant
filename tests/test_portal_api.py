import importlib

from fastapi.testclient import TestClient


def get_app(tmp_path, monkeypatch):
    monkeypatch.setenv("DATABASE_URL", f"sqlite:///{tmp_path}/db.sqlite")
    module = importlib.import_module("services.portal_api.main")
    importlib.reload(module)
    return module.app


def test_crud_lifecycle(tmp_path, monkeypatch):
    app = get_app(tmp_path, monkeypatch)
    client = TestClient(app)

    resp = client.post("/drafts", json={"draft": "a", "copy": "b"})
    assert resp.status_code == 200
    created = resp.json()
    assert created["draft"] == "a"
    draft_id = created["id"]

    resp = client.get(f"/drafts/{draft_id}")
    assert resp.status_code == 200

    resp = client.put(f"/drafts/{draft_id}", json={"draft": "c", "copy": "d"})
    assert resp.status_code == 200
    updated = resp.json()
    assert updated["draft"] == "c"

    resp = client.delete(f"/drafts/{draft_id}")
    assert resp.status_code == 200
    resp = client.get(f"/drafts/{draft_id}")
    assert resp.status_code == 404
