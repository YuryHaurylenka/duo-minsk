from datetime import datetime, timezone
from decimal import Decimal
from types import SimpleNamespace
from unittest.mock import MagicMock
from uuid import uuid4

from fastapi.testclient import TestClient

from app.auth import AuthUser, require_user
from app.database import get_db
from app.main import app
from app.models.entities import Couple, CoupleMember, Place

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


def test_match_payload_hides_partner_likes_until_mutual_match():
    from app.main import _match_session_payload

    session_id = uuid4()
    candidate = {
        "slug": "quiet-cafe",
        "name": "Quiet Cafe",
        "my_vote": False,
        "partner_vote": None,
        "partner_has_voted": True,
    }
    db = MagicMock()
    session_result = MagicMock()
    session_result.mappings.return_value.first.return_value = {
        "id": session_id, "status": "active", "city_slug": "minsk",
        "created_at": datetime.now(timezone.utc),
    }
    candidates_result = MagicMock()
    candidates_result.mappings.return_value.all.return_value = [candidate]
    db.execute.side_effect = [session_result, candidates_result]
    couple = Couple(id=COUPLE_ID, name="Us", invite_code="ABC123", created_by=USER_ID,
                    created_at=datetime.now(timezone.utc))

    result = _match_session_payload(session_id, AuthUser(id=USER_ID, email="test@example.com"), couple, db)

    assert result["candidates"][0]["my_vote"] is False
    assert result["candidates"][0]["partner_vote"] is None
    assert result["partner_votes"] == 1
    assert result["matches"] == []
    query = str(db.execute.call_args_list[1].args[0])
    assert "CASE" in query
    assert "partner_has_voted" in query


def test_match_payload_reveals_only_mutual_likes():
    from app.main import _match_session_payload

    session_id = uuid4()
    candidate = {
        "slug": "quiet-cafe",
        "name": "Quiet Cafe",
        "my_vote": True,
        "partner_vote": True,
        "partner_has_voted": True,
    }
    db = MagicMock()
    session_result = MagicMock()
    session_result.mappings.return_value.first.return_value = {
        "id": session_id, "status": "active", "city_slug": "minsk",
        "created_at": datetime.now(timezone.utc),
    }
    candidates_result = MagicMock()
    candidates_result.mappings.return_value.all.return_value = [candidate]
    db.execute.side_effect = [session_result, candidates_result]
    couple = Couple(id=COUPLE_ID, name="Us", invite_code="ABC123", created_by=USER_ID,
                    created_at=datetime.now(timezone.utc))

    result = _match_session_payload(session_id, AuthUser(id=USER_ID, email="test@example.com"), couple, db)

    assert len(result["matches"]) == 1
    assert result["matches"][0]["slug"] == "quiet-cafe"
    assert result["partner_votes"] == 1

def test_match_active_session_lookup_returns_current_couple_round():
    session_id = uuid4()
    db = MagicMock()
    db.scalar.return_value = CoupleMember(couple_id=COUPLE_ID, user_id=USER_ID, role="owner")
    db.get.side_effect = [
        Couple(id=COUPLE_ID, name="Us", invite_code="ABC123", created_by=USER_ID,
               created_at=datetime.now(timezone.utc)),
        SimpleNamespace(slug="minsk", is_active=True),
    ]
    active = {"id": session_id, "status": "active", "city_slug": "minsk"}
    result = MagicMock()
    result.mappings.return_value.first.return_value = active
    db.execute.return_value = result
    app.dependency_overrides[get_db] = lambda: db
    app.dependency_overrides[require_user] = lambda: AuthUser(id=USER_ID, email="test@example.com")
    try:
        response = TestClient(app).get("/api/match/sessions/active?city_slug=minsk")
    finally:
        app.dependency_overrides.clear()
    assert response.status_code == 200
    assert response.json() == {"active": True, "id": str(session_id), "status": "active", "city_slug": "minsk"}


def test_match_active_session_lookup_returns_empty_when_round_missing():
    db = MagicMock()
    db.scalar.return_value = CoupleMember(couple_id=COUPLE_ID, user_id=USER_ID, role="owner")
    db.get.side_effect = [
        Couple(id=COUPLE_ID, name="Us", invite_code="ABC123", created_by=USER_ID,
               created_at=datetime.now(timezone.utc)),
        SimpleNamespace(slug="minsk", is_active=True),
    ]
    result = MagicMock()
    result.mappings.return_value.first.return_value = None
    db.execute.return_value = result
    app.dependency_overrides[get_db] = lambda: db
    app.dependency_overrides[require_user] = lambda: AuthUser(id=USER_ID, email="test@example.com")
    try:
        response = TestClient(app).get("/api/match/sessions/active?city_slug=minsk")
    finally:
        app.dependency_overrides.clear()
    assert response.status_code == 200
    assert response.json() == {"active": False}

def test_couple_analytics_returns_shared_activity_and_match_history():
    db = MagicMock()
    db.scalar.return_value = CoupleMember(couple_id=COUPLE_ID, user_id=USER_ID, role="owner")
    db.get.return_value = Couple(id=COUPLE_ID, name="Us", invite_code="ABC123", created_by=USER_ID,
                                 created_at=datetime.now(timezone.utc))
    activity = MagicMock()
    activity.mappings.return_value.one.return_value = {
        "favorites": 3, "visits": 2, "ratings": 1, "average_rating": 4.0
    }
    categories = MagicMock()
    categories.mappings.return_value.all.return_value = [{"name": "Кофейни", "value": 2}]
    match_stats = MagicMock()
    match_stats.mappings.return_value.one.return_value = {
        "rounds": 4, "completed_rounds": 3, "mutual_matches": 5
    }
    history = MagicMock()
    history.mappings.return_value.all.return_value = [{
        "id": "session-1", "status": "completed", "city_slug": "minsk",
        "created_at": datetime.now(timezone.utc), "mutual_matches": 2
    }]
    db.execute.side_effect = [activity, categories, match_stats, history]
    app.dependency_overrides[get_db] = lambda: db
    app.dependency_overrides[require_user] = lambda: AuthUser(id=USER_ID, email="test@example.com")
    try:
        response = TestClient(app).get("/api/analytics/couple")
    finally:
        app.dependency_overrides.clear()
    assert response.status_code == 200
    payload = response.json()
    assert payload["activity"]["visits"] == 2
    assert payload["common_interests"] == [{"name": "Кофейни", "value": 2}]
    assert payload["match_stats"]["mutual_matches"] == 5
    assert payload["match_history"][0]["status"] == "completed"



def test_couple_preferences_are_scoped_to_current_member_and_partner():
    db = MagicMock()
    db.scalar.return_value = CoupleMember(couple_id=COUPLE_ID, user_id=USER_ID, role="owner")
    db.get.return_value = Couple(id=COUPLE_ID, name="Us", invite_code="ABC123", created_by=USER_ID,
                                 created_at=datetime.now(timezone.utc))
    result = MagicMock()
    partner_id = uuid4()
    result.mappings.return_value.one.return_value = {
        "preferences": {
            "members": {
                str(USER_ID): {"interests": ["Кофейни"], "avoid": []},
                str(partner_id): {"interests": ["Культура"], "avoid": ["Бары и пабы"]},
            }
        },
        "member_ids": [str(USER_ID), str(partner_id)],
    }
    db.execute.return_value = result
    app.dependency_overrides[get_db] = lambda: db
    app.dependency_overrides[require_user] = lambda: AuthUser(id=USER_ID, email="test@example.com")
    try:
        response = TestClient(app).get("/api/couples/preferences")
    finally:
        app.dependency_overrides.clear()
    assert response.status_code == 200
    assert response.json()["mine"] == {"interests": ["Кофейни"], "avoid": []}
    assert response.json()["partner"]["interests"] == ["Культура"]


def test_couple_preferences_update_only_current_member():
    db = MagicMock()
    db.scalar.return_value = CoupleMember(couple_id=COUPLE_ID, user_id=USER_ID, role="owner")
    db.get.return_value = Couple(id=COUPLE_ID, name="Us", invite_code="ABC123", created_by=USER_ID,
                                 created_at=datetime.now(timezone.utc))
    updated = MagicMock()
    updated.mappings.return_value.one.return_value = {
        "preferences": {"members": {str(USER_ID): {"interests": ["Рестораны"], "avoid": []}}},
        "member_ids": [str(USER_ID)],
    }
    db.execute.side_effect = [MagicMock(), updated]
    app.dependency_overrides[get_db] = lambda: db
    app.dependency_overrides[require_user] = lambda: AuthUser(id=USER_ID, email="test@example.com")
    try:
        response = TestClient(app).put(
            "/api/couples/preferences",
            json={"interests": ["Рестораны"], "avoid": []},
        )
    finally:
        app.dependency_overrides.clear()
    assert response.status_code == 200
    assert response.json() == {"mine": {"interests": ["Рестораны"], "avoid": []}, "partner": None}
    assert "private.set_couple_member_preferences" in str(db.execute.call_args_list[0].args[0])
    assert db.commit.called


def test_couple_preferences_reject_unknown_categories():
    db = MagicMock()
    db.scalar.return_value = CoupleMember(couple_id=COUPLE_ID, user_id=USER_ID, role="owner")
    db.get.return_value = Couple(id=COUPLE_ID, name="Us", invite_code="ABC123", created_by=USER_ID,
                                 created_at=datetime.now(timezone.utc))
    app.dependency_overrides[get_db] = lambda: db
    app.dependency_overrides[require_user] = lambda: AuthUser(id=USER_ID, email="test@example.com")
    try:
        response = TestClient(app).put(
            "/api/couples/preferences",
            json={"interests": ["Secret"], "avoid": []},
        )
    finally:
        app.dependency_overrides.clear()
    assert response.status_code == 422
    db.execute.assert_not_called()


def _recommendation_place(slug, name, category, rating):
    return Place(
        id=uuid4(), slug=slug, city_slug="minsk", name=name, category=category,
        emoji="✨", description="A good place", address="Minsk", rating=rating,
        reviews="100", price_label="20 BYN", couple_price_label="40 BYN",
        level=1, risk="good", tip="", website_url="", source_name="", source_url="",
        cost=Decimal("20"),
    )


def test_recommendations_combine_both_partners_preferences_and_activity():
    db = MagicMock()
    partner_id = uuid4()
    db.scalar.return_value = CoupleMember(couple_id=COUPLE_ID, user_id=USER_ID, role="owner")
    db.get.side_effect = [SimpleNamespace(slug="minsk", is_active=True), Couple(id=COUPLE_ID, name="Us", invite_code="ABC123", created_by=USER_ID,
                                 created_at=datetime.now(timezone.utc))]
    preferences = MagicMock()
    preferences.mappings.return_value.one.return_value = {
        "preferences": {
            "members": {
                str(USER_ID): {"interests": ["Кофейни"], "avoid": []},
                str(partner_id): {"interests": ["Кофейни"], "avoid": ["Бары и пабы"]},
                str(uuid4()): {"interests": [], "avoid": ["Активности"]},
            }
        },
        "member_ids": [str(USER_ID), str(partner_id)],
    }
    matches = MagicMock()
    matches.scalars.return_value.all.return_value = ["shared-cafe"]
    db.execute.side_effect = [preferences, matches]
    activity_rows = MagicMock()
    activity_rows.all.return_value = [
        SimpleNamespace(place_slug="old-cafe", is_favorite=True, visited_at=None, rating=5)
    ]
    places_rows = MagicMock()
    places_rows.all.return_value = [
        _recommendation_place("old-cafe", "Old Coffee", "Кофейни", "4.8"),
        _recommendation_place("shared-cafe", "Common Coffee", "Кофейни", "4.8"),
        _recommendation_place("bar-place", "Cocktail Bar", "Пабы и бары", "4.9"),
        _recommendation_place("game-place", "Game Room", "Игры", "4.2"),
        _recommendation_place("unsafe-place", "Unsafe Attraction", "Игры", "4.9"),
    ]
    places_rows.all.return_value[-1].risk = "avoid"
    def scalars_for_recommendations(statement):
        statement_text = str(statement).lower()
        if "place_activity" in statement_text:
            return activity_rows
        if "places" in statement_text:
            return places_rows
        raise AssertionError(f"Unexpected recommendation query: {statement_text}")

    db.scalars.side_effect = scalars_for_recommendations
    app.dependency_overrides[get_db] = lambda: db
    app.dependency_overrides[require_user] = lambda: AuthUser(id=USER_ID, email="test@example.com")
    try:
        response = TestClient(app).post(
            "/api/recommendations",
            json={"city_slug": "minsk", "interests": [], "avoid": [], "limit": 6},
        )
    finally:
        app.dependency_overrides.clear()
    assert response.status_code == 200
    payload = response.json()
    assert payload["context"]["is_couple"] is True
    assert payload["items"][0]["slug"] == "shared-cafe"
    assert "Интересно обоим" in payload["items"][0]["reasons"]
    assert "Вы оба выбрали это в DUO Match" in payload["items"][0]["reasons"]
    assert "Вам нравятся места этой категории" in payload["items"][0]["reasons"]
    assert "old-cafe" not in [item["slug"] for item in payload["items"]]
    assert "bar-place" not in [item["slug"] for item in payload["items"]]
    assert "game-place" in [item["slug"] for item in payload["items"]]
    assert "unsafe-place" not in [item["slug"] for item in payload["items"]]



def test_recommendation_feedback_is_private_and_idempotent():
    db = MagicMock()
    db.scalar.return_value = "shared-cafe"
    app.dependency_overrides[get_db] = lambda: db
    app.dependency_overrides[require_user] = lambda: AuthUser(id=USER_ID, email="test@example.com")
    try:
        response = TestClient(app).post("/api/recommendations/shared-cafe/dismiss")
    finally:
        app.dependency_overrides.clear()
    assert response.status_code == 204
    db.execute.assert_called_once()
    db.commit.assert_called_once()


def test_recommendation_feedback_rejects_unknown_place():
    db = MagicMock()
    db.scalar.return_value = None
    app.dependency_overrides[get_db] = lambda: db
    app.dependency_overrides[require_user] = lambda: AuthUser(id=USER_ID, email="test@example.com")
    try:
        response = TestClient(app).post("/api/recommendations/not-a-place/dismiss")
    finally:
        app.dependency_overrides.clear()
    assert response.status_code == 404
    db.execute.assert_not_called()


def test_recommendations_reject_unknown_interest_categories():
    db = MagicMock()
    app.dependency_overrides[get_db] = lambda: db
    app.dependency_overrides[require_user] = lambda: AuthUser(id=USER_ID, email="test@example.com")
    try:
        response = TestClient(app).post(
            "/api/recommendations",
            json={"city_slug": "minsk", "interests": ["Secret"], "avoid": [], "limit": 6},
        )
    finally:
        app.dependency_overrides.clear()
    assert response.status_code == 422
