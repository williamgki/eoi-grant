import importlib

from fastapi.testclient import TestClient


def get_app(tmp_path, monkeypatch):
    monkeypatch.setenv("DATABASE_URL", f"sqlite:///{tmp_path}/db.sqlite")
    monkeypatch.setenv("UPLOAD_DIR", str(tmp_path / "uploads"))
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


def test_upload_endpoint(tmp_path, monkeypatch):
    captured = {}

    def dummy_load_dataframe(df):
        captured["rows"] = list(df["name"])

    monkeypatch.setattr(
        importlib.import_module("scripts.csv_loader"),
        "load_dataframe",
        dummy_load_dataframe,
    )

    app = get_app(tmp_path, monkeypatch)
    client = TestClient(app)

    csv_content = "submitted_at,name\n01/01/24 10:00:00,Tester\n"
    resp = client.post(
        "/upload",
        files={"file": ("data.csv", csv_content, "text/csv")},
    )
    assert resp.status_code == 200
    assert captured.get("rows") == ["Tester"]
    upload_path = tmp_path / "uploads" / "data.csv"
    assert upload_path.exists()
