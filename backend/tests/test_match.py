from datetime import datetime, timezone
from types import SimpleNamespace
from unittest.mock import MagicMock
from uuid import uuid4

from fastapi.testclient import TestClient

from app.auth import AuthUser, require_user
from app.database import get_db
from app.main import app
from app.models.entities import Couple, CoupleMember

USER_ID = uuid4()
COUPLE_ID = uuid4()


def test_match_requires_second_member():
    db = MagicMock()
    db.scalar.side_effect = [CoupleMember(couple_id=COUPLE_ID, user_id=USER_ID, role="owner"), 1]
    db.get.return_value = Couple(id=COUPLE_ID, name="Us", invite_code="ABC123", created_by=USER_ID,
                                 created_at=datetime.now(timezone.utc))
    app.dependency_overrides[get_db] = lambda: db
    app.dependency_overrides[require_user] = lambda: AuthUser(id=USER_ID, email="test@example.com")
    try:
        response = TestClient(app).post("/api/match/sessions", json={"city_slug": "minsk"})
    finally:
        app.dependency_overrides.clear()
    assert response.status_code == 409
    assert "второго участника" in response.json()["detail"]
    db.execute.assert_not_called()


def test_match_session_rejects_too_few_candidates():
    db = MagicMock()
    db.scalar.side_effect = [CoupleMember(couple_id=COUPLE_ID, user_id=USER_ID, role="owner"), 2]
    db.get.side_effect = [
        Couple(id=COUPLE_ID, name="Us", invite_code="ABC123", created_by=USER_ID,
               created_at=datetime.now(timezone.utc)),
        SimpleNamespace(slug="minsk", is_active=True),
    ]
    active_result = MagicMock()
    active_result.mappings.return_value.first.return_value = None
    places_result = MagicMock()
    places_result.scalars.return_value.all.return_value = ["one-place"]
    db.execute.side_effect = [active_result, places_result]
    app.dependency_overrides[get_db] = lambda: db
    app.dependency_overrides[require_user] = lambda: AuthUser(id=USER_ID, email="test@example.com")
    try:
        response = TestClient(app).post("/api/match/sessions", json={"city_slug": "minsk", "limit": 8})
    finally:
        app.dependency_overrides.clear()
    assert response.status_code == 422
    assert "Недостаточно мест" in response.json()["detail"]
    db.commit.assert_not_called()


def test_match_start_resumes_active_session_for_partner():
    session_id = uuid4()
    db = MagicMock()
    db.scalar.side_effect = [CoupleMember(couple_id=COUPLE_ID, user_id=USER_ID, role="owner"), 2]
    db.get.side_effect = [
        Couple(id=COUPLE_ID, name="Us", invite_code="ABC123", created_by=USER_ID,
               created_at=datetime.now(timezone.utc)),
        SimpleNamespace(slug="minsk", is_active=True),
    ]
    active = {"id": session_id, "status": "active", "city_slug": "minsk", "candidate_count": 24}
    active_result = MagicMock()
    active_result.mappings.return_value.first.return_value = active
    db.execute.return_value = active_result
    app.dependency_overrides[get_db] = lambda: db
    app.dependency_overrides[require_user] = lambda: AuthUser(id=USER_ID, email="test@example.com")
    try:
        response = TestClient(app).post("/api/match/sessions", json={"city_slug": "minsk"})
    finally:
        app.dependency_overrides.clear()
    assert response.status_code == 201
    assert response.json()["id"] == str(session_id)
    assert response.json()["resumed"] is True
    db.commit.assert_not_called()
