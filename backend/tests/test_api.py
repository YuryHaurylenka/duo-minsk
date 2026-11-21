from datetime import date, datetime, timezone
from decimal import Decimal
from types import SimpleNamespace
from unittest.mock import MagicMock
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient

from app.auth import AuthUser, get_current_user, require_user
from app.database import get_db
from app.main import app
from app.models.entities import City, Couple, CoupleMember, DuoDatePlan, Place


USER_ID = uuid4()
COUPLE_ID = uuid4()
PLACE_SLUG = "test-cafe"


@pytest.fixture
def db():
    return MagicMock()


@pytest.fixture
def client(db):
    app.dependency_overrides[get_db] = lambda: db
    app.dependency_overrides[require_user] = lambda: AuthUser(id=USER_ID, email="test@example.com")
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


def membership(couple_id=COUPLE_ID, user_id=USER_ID, role="owner"):
    return CoupleMember(couple_id=couple_id, user_id=user_id, role=role)


def couple(couple_id=COUPLE_ID):
    return Couple(id=couple_id, name="Us", invite_code="ABC123", created_by=USER_ID,
                  created_at=datetime.now(timezone.utc))


def test_health_is_public():
    response = TestClient(app).get("/api/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok", "service": "duo-api", "version": "2.0.0"}


def test_me_returns_user_without_couple(client, db):
    db.scalar.return_value = None
    response = client.get("/api/me")
    assert response.status_code == 200
    assert response.json() == {"id": str(USER_ID), "email": "test@example.com", "couple": None}


def test_me_returns_couple_membership(client, db):
    db.scalar.return_value = membership()
    db.get.return_value = couple()
    response = client.get("/api/me")
    assert response.status_code == 200
    assert response.json()["couple"] == {
        "id": str(COUPLE_ID), "name": "Us", "invite_code": "ABC123", "role": "owner"
    }


def test_create_couple_calls_database_rpc(client, db):
    db.scalar.return_value = None
    db.execute.return_value.mappings.return_value.one.return_value = {
        "id": COUPLE_ID, "name": "Our duo", "invite_code": "ABC123"
    }
    response = client.post("/api/couples", json={"name": "  Our duo  "})
    assert response.status_code == 201
    assert response.json()["invite_code"] == "ABC123"
    assert "private.create_couple" in str(db.execute.call_args.args[0])
    db.commit.assert_called_once()


def test_user_cannot_create_second_couple(client, db):
    db.scalar.return_value = membership()
    response = client.post("/api/couples", json={"name": "Another"})
    assert response.status_code == 409
    db.execute.assert_not_called()


def test_join_couple_normalizes_invite_code(client, db):
    db.scalar.return_value = None
    db.execute.return_value.mappings.return_value.one.return_value = {
        "id": COUPLE_ID, "name": "Us", "invite_code": "ABC123"
    }
    response = client.post("/api/couples/join", json={"invite_code": " abc123 "})
    assert response.status_code == 200
    assert response.json()["role"] == "member"
    assert "private.join_couple" in str(db.execute.call_args.args[0])
    assert db.execute.call_args.args[1] == {"code": "ABC123"}


def test_join_rejects_user_already_in_couple(client, db):
    db.scalar.return_value = membership()
    response = client.post("/api/couples/join", json={"invite_code": "ABC123"})
    assert response.status_code == 409
    db.execute.assert_not_called()


def test_join_returns_not_found_for_unknown_invite(client, db):
    db.scalar.return_value = None
    db.execute.side_effect = RuntimeError("unknown invite")
    response = client.post("/api/couples/join", json={"invite_code": "ABC123"})
    assert response.status_code == 404
    db.rollback.assert_called_once()


def test_leave_couple_removes_only_current_membership(client, db):
    db.scalar.return_value = membership()
    response = client.delete("/api/couples/me")
    assert response.status_code == 204
    db.execute.assert_called_once()
    db.commit.assert_called_once()


def test_leave_couple_returns_not_found_without_membership(client, db):
    db.scalar.return_value = None
    response = client.delete("/api/couples/me")
    assert response.status_code == 404
    db.execute.assert_not_called()


def test_activity_is_available_for_personal_account(client, db):
    db.scalar.return_value = None
    db.scalars.return_value.all.return_value = []
    response = client.get("/api/activity")
    assert response.status_code == 200
    assert response.json() == []


def test_activity_returns_couple_records(client, db):
    db.scalar.return_value = membership()
    db.get.return_value = couple()
    db.scalars.return_value.all.return_value = [SimpleNamespace(
        place_slug=PLACE_SLUG, place_name="Cafe", is_favorite=True, visited_at=None, rating=5, note="Great"
    )]
    response = client.get("/api/activity")
    assert response.status_code == 200
    assert response.json() == [{
        "place_slug": PLACE_SLUG, "place_name": "Cafe", "is_favorite": True, "visited_at": None, "rating": 5, "note": "Great"
    }]


def test_activity_sync_upserts_known_places_and_ignores_unknown(client, db):
    db.scalar.return_value = membership()
    db.get.return_value = couple()
    db.scalars.return_value.all.return_value = [Place(slug=PLACE_SLUG, name="Test Cafe")]
    response = client.put("/api/activity", json=[
        {"place_slug": PLACE_SLUG, "is_favorite": True, "visited": True, "rating": 5},
        {"place_slug": "missing-place", "is_favorite": True}
    ])
    assert response.status_code == 204
    assert db.execute.call_count == 1
    db.commit.assert_called_once()



def test_personal_activity_sync_upserts_for_user_without_couple(client, db):
    db.scalar.return_value = None
    db.scalars.return_value.all.return_value = [Place(slug=PLACE_SLUG, name="Test Cafe")]
    response = client.put("/api/activity", json=[
        {"place_slug": PLACE_SLUG, "is_favorite": True, "visited": True, "rating": 5, "note": "Great"}
    ])
    assert response.status_code == 204
    db.execute.assert_called_once()
    db.commit.assert_called_once()

def test_activity_rating_must_be_between_one_and_five(client, db):
    response = client.put("/api/activity", json=[{"place_slug": PLACE_SLUG, "rating": 6}])
    assert response.status_code == 422


def test_plans_requires_membership(client, db):
    db.scalar.return_value = None
    response = client.get("/api/plans")
    assert response.status_code == 409


def test_create_plan_persists_for_current_couple(client, db):
    db.scalar.return_value = membership()
    db.get.return_value = couple()
    response = client.post("/api/plans", json={
        "plan_date": "2026-12-01", "title": "Dinner", "mood": "romantic",
        "budget": "75.50", "items": [{"place": PLACE_SLUG, "time": "18:00", "duration_minutes": 60, "estimated_cost": 75.5}], "notes": "Book a table"
    })
    assert response.status_code == 201
    assert response.json()["title"] == "Dinner"
    assert response.json()["budget"] == "75.50"
    assert response.json()["items"][0]["time"] == "18:00"
    assert response.json()["items"][0]["duration_minutes"] == 60
    db.add.assert_called_once()
    db.commit.assert_called_once()


def test_update_plan_persists_reordered_items_for_current_couple(client, db):
    plan = SimpleNamespace(
        id=uuid4(), plan_date=date(2026, 12, 1), title="Dinner", mood="romantic",
        budget=Decimal("75.50"), items=[{"place": "first"}], notes="",
        created_at=datetime.now(timezone.utc), updated_at=datetime.now(timezone.utc), updated_by=None,
    )
    db.scalar.side_effect = [membership(), plan]
    db.get.return_value = couple()
    response = client.patch(f"/api/plans/{plan.id}", json={
        "expected_updated_at": plan.updated_at.isoformat(),
        "items": [{"place": "second"}, {"place": "first"}], "notes": "Meet at 18:00"
    })
    assert response.status_code == 200
    assert [item["place"] for item in response.json()["items"]] == ["second", "first"]
    assert response.json()["notes"] == "Meet at 18:00"
    assert response.json()["updated_at"] is not None
    assert response.json()["updated_by"] == str(USER_ID)
    db.commit.assert_called_once()
    db.refresh.assert_called_once_with(plan)



def test_update_plan_records_authenticated_editor(client, db):
    editor_id = uuid4()
    plan = SimpleNamespace(
        id=uuid4(), plan_date=date(2026, 12, 1), title="Dinner", mood="romantic",
        budget=Decimal("75.50"), items=[], notes="",
        created_at=datetime.now(timezone.utc), updated_at=datetime.now(timezone.utc), updated_by=None,
    )
    db.scalar.side_effect = [membership(), plan]
    db.get.return_value = couple()
    response = client.patch(f"/api/plans/{plan.id}", json={
        "expected_updated_at": plan.updated_at.isoformat(), "title": "Updated dinner"
    })
    assert response.status_code == 200
    assert plan.updated_by is not None
    assert response.json()["updated_by"] == str(plan.updated_by)


def test_update_plan_rejects_stale_version(client, db):
    current_version = datetime(2026, 11, 21, 18, 0, tzinfo=timezone.utc)
    plan = SimpleNamespace(
        id=uuid4(), plan_date=date(2026, 12, 1), title="Latest title", mood="romantic",
        budget=Decimal("75.50"), items=[{"place": "latest"}], notes="",
        created_at=current_version, updated_at=current_version,
    )
    db.scalar.side_effect = [membership(), plan]
    db.get.return_value = couple()
    response = client.patch(f"/api/plans/{plan.id}", json={
        "expected_updated_at": "2026-11-21T17:59:00Z",
        "title": "Stale overwrite",
    })
    assert response.status_code == 409
    assert "изменён другим участником" in response.json()["detail"]
    assert plan.title == "Latest title"
    db.commit.assert_not_called()

def test_update_plan_is_scoped_to_current_couple(client, db):
    db.scalar.side_effect = [membership(), None]
    db.get.return_value = couple()
    response = client.patch(f"/api/plans/{uuid4()}", json={
        "expected_updated_at": datetime.now(timezone.utc).isoformat(), "title": "Not ours"
    })
    assert response.status_code == 404
    db.commit.assert_not_called()


def test_update_plan_requires_version_token(client, db):
    response = client.patch(f"/api/plans/{uuid4()}", json={"title": "Missing version"})
    assert response.status_code == 422
    assert "expected_updated_at" in str(response.json()["detail"])
    db.scalar.assert_not_called()


def test_update_plan_rejects_empty_patch(client, db):
    plan = SimpleNamespace(id=uuid4())
    db.scalar.side_effect = [membership(), plan]
    db.get.return_value = couple()
    response = client.patch(f"/api/plans/{plan.id}", json={})
    assert response.status_code == 422
    db.commit.assert_not_called()


def test_create_plan_rejects_invalid_budget(client, db):
    response = client.post("/api/plans", json={
        "plan_date": "2026-12-01", "title": "Dinner", "budget": -1
    })
    assert response.status_code == 422


def test_delete_plan_is_scoped_to_current_couple(client, db):
    db.scalar.return_value = membership()
    db.get.return_value = couple()
    db.scalar.side_effect = [membership(), None]
    response = client.delete(f"/api/plans/{uuid4()}")
    assert response.status_code == 404
    db.delete.assert_not_called()


def test_delete_plan_deletes_matching_plan(client, db):
    plan = SimpleNamespace(id=uuid4())
    db.scalar.side_effect = [membership(), plan]
    db.get.return_value = couple()
    response = client.delete(f"/api/plans/{plan.id}")
    assert response.status_code == 204
    db.delete.assert_called_once_with(plan)
    db.commit.assert_called_once()


def test_protected_endpoint_rejects_missing_bearer_token(db):
    from fastapi.testclient import TestClient
    app.dependency_overrides[get_db] = lambda: db
    try:
        response = TestClient(app).get("/api/me")
    finally:
        app.dependency_overrides.clear()
    assert response.status_code == 401
    assert response.json()["detail"] == "Требуется авторизация"


def test_protected_endpoint_rejects_invalid_bearer_token(db):
    from fastapi.testclient import TestClient
    app.dependency_overrides[get_db] = lambda: db
    try:
        response = TestClient(app).get("/api/me", headers={"Authorization": "Bearer not-a-jwt"})
    finally:
        app.dependency_overrides.clear()
    assert response.status_code == 401
    assert response.json()["detail"] == "Недействительная или истёкшая сессия"


def test_join_returns_conflict_when_couple_is_full(client, db):
    db.scalar.return_value = None
    db.execute.side_effect = RuntimeError("В паре уже два участника")
    response = client.post("/api/couples/join", json={"invite_code": "ABC123"})
    assert response.status_code == 409
    assert response.json()["detail"] == "В этой паре уже два участника"


def test_valid_supabase_hs256_token_sets_authenticated_database_role(db, monkeypatch):
    import jwt
    from datetime import timedelta
    from fastapi.security import HTTPAuthorizationCredentials
    import app.auth as auth_module

    secret = "ci-test-secret-that-is-not-used-in-production"
    issuer = "https://example.supabase.co/auth/v1"
    monkeypatch.setattr(auth_module, "get_settings", lambda: SimpleNamespace(
        supabase_url="https://example.supabase.co", supabase_jwt_secret=secret
    ))
    token = jwt.encode({
        "sub": str(USER_ID), "email": "test@example.com", "role": "authenticated",
        "aud": "authenticated", "iss": issuer,
        "exp": datetime.now(timezone.utc) + timedelta(minutes=5)
    }, secret, algorithm="HS256")
    user = get_current_user(
        credentials=HTTPAuthorizationCredentials(scheme="Bearer", credentials=token), db=db
    )
    assert user == AuthUser(id=USER_ID, email="test@example.com")
    assert db.execute.call_count == 4


def test_create_couple_handles_concurrent_membership_conflict(client, db):
    db.scalar.return_value = None
    db.execute.side_effect = RuntimeError('duplicate key violates unique constraint "couple_members_user_id_key"')
    response = client.post("/api/couples", json={"name": "Race"})
    assert response.status_code == 409
    assert response.json()["detail"] == "Вы уже состоите в паре"
    db.rollback.assert_called_once()


def test_join_couple_handles_concurrent_membership_conflict(client, db):
    db.scalar.return_value = None
    db.execute.side_effect = RuntimeError('duplicate key violates unique constraint "couple_members_user_id_key"')
    response = client.post("/api/couples/join", json={"invite_code": "ABC123"})
    assert response.status_code == 409
    assert response.json()["detail"] == "Вы уже состоите в паре"
    db.rollback.assert_called_once()



def city_fixture(slug="minsk", active=True):
    return City(slug=slug, name="Minsk", name_localized="Минск", country_code="BY",
                country_name="Belarus", country_name_localized="Беларусь", timezone="Europe/Minsk",
                currency_code="BYN", default_language="ru", is_active=active)


def test_list_cities_returns_active_city_catalog(client, db):
    db.scalars.return_value.all.return_value = [city_fixture()]
    response = client.get("/api/cities")
    assert response.status_code == 200
    assert response.json() == [{
        "slug": "minsk", "name": "Minsk", "name_localized": "Минск", "country_code": "BY",
        "country_name": "Belarus", "country_name_localized": "Беларусь", "timezone": "Europe/Minsk",
        "currency_code": "BYN", "default_language": "ru"
    }]


def test_places_are_scoped_to_requested_city(client, db):
    db.get.return_value = city_fixture()
    db.scalars.return_value.all.return_value = []
    response = client.get("/api/places?city=minsk")
    assert response.status_code == 200
    assert response.json() == []
    db.get.assert_called_once_with(City, "minsk")


def test_places_include_coordinates_for_map(client, db):
    db.get.return_value = city_fixture()
    place = SimpleNamespace(
        id=uuid4(), slug="map-cafe", city_slug="minsk", name="Map Cafe", category="Кофейни",
        emoji="☕", description="Coffee", address="пр-т Независимости, 1, Минск", rating="—",
        reviews="—", price_label="Уточнить", couple_price_label="Уточнить", level=1,
        risk="good", tip="", website_url="", source_name="OSM", source_url="", cost=None,
        latitude=53.9001, longitude=27.5601, location_verified_at=None,
    )
    db.scalars.return_value.all.return_value = [place]
    response = client.get("/api/places?city=minsk")
    assert response.status_code == 200
    assert response.json()[0]["latitude"] == 53.9001
    assert response.json()[0]["longitude"] == 27.5601
    assert response.json()[0]["location_verified_at"] is None


def test_places_reject_unknown_or_inactive_city(client, db):
    db.get.return_value = None
    response = client.get("/api/places?city=unknown-city")
    assert response.status_code == 404
    assert response.json()["detail"] == "Город пока недоступен"


def test_events_reject_unknown_city(client, db):
    db.get.return_value = None
    response = client.get("/api/events?city=unknown-city")
    assert response.status_code == 404


def test_updates_are_scoped_to_requested_city(client, db):
    db.get.return_value = city_fixture()
    db.scalars.return_value.all.return_value = []
    response = client.get("/api/updates?city=minsk")
    assert response.status_code == 200
    assert response.json() == []



def test_readiness_reports_database_and_active_cities(client, db):
    db.scalar.return_value = 1
    response = client.get("/api/health/ready")
    assert response.status_code == 200
    assert response.json() == {"status": "ready", "database": "ok", "active_cities": 1}
    db.execute.assert_called_once()


def test_readiness_returns_503_when_database_is_unavailable(client, db):
    from sqlalchemy.exc import SQLAlchemyError
    db.execute.side_effect = SQLAlchemyError("database offline")
    response = client.get("/api/health/ready")
    assert response.status_code == 503
    assert response.json()["detail"] == "Database unavailable"
