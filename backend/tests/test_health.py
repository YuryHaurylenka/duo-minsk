from fastapi.testclient import TestClient
from app.main import app


def test_health():
    response = TestClient(app).get("/api/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_vite_assets_are_served():
    """Vite bundles must be served as static files, not routed into the API."""
    from pathlib import Path

    assets_dir = Path(__file__).resolve().parents[2] / "public" / "assets"
    asset = next(assets_dir.iterdir())
    response = TestClient(app).get(f"/assets/{asset.name}")

    assert response.status_code == 200
    assert response.content
