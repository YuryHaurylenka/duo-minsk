from contextlib import asynccontextmanager
import json
from datetime import date, datetime, time, timedelta, timezone
from zoneinfo import ZoneInfo
from decimal import Decimal
from uuid import UUID, uuid4
from fastapi import FastAPI, Depends, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import select, func, or_, text, delete
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from app.config import get_settings
from app.database import get_db
from app.auth import AuthUser, require_user, require_match_user
from app.models.entities import City, Place, Couple, CoupleMember, PlaceActivity, PersonalPlaceActivity, RecommendationFeedback, DuoEvent, DuoDatePlan, DuoPlaceUpdate
from app.schemas import CityOut, PlaceOut, EventOut, PlaceUpdateOut, CoupleCreate, CoupleJoin, CoupleOut, CouplePreferencesIn, RecommendationRequest, ActivitySyncItem, PlanCreate, PlanUpdate, PlanOut, MatchSessionCreate, MatchVoteIn

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Schema is managed by Alembic migrations; never create tables at runtime.
    yield


app = FastAPI(title="DUO API", version="2.0.0", description="Backend для DUO — city discovery and shared date planning", lifespan=lifespan)
app.add_middleware(CORSMiddleware, allow_origins=settings.allowed_origins, allow_credentials=True, allow_methods=["*"], allow_headers=["*"])


# Serve Vite's generated assets directly from the public directory.
# Keep the directory literal so Vercel's FastAPI static-file collector can
# discover the mount and promote the files to its CDN at build time.
from fastapi.staticfiles import StaticFiles

app.mount("/assets", StaticFiles(directory="public/assets", check_dir=False), name="assets")


def get_couple(db: Session, user: AuthUser) -> Couple:
    member = db.scalar(select(CoupleMember).where(CoupleMember.user_id == user.id).limit(1))
    if not member:
        raise HTTPException(status_code=409, detail="Сначала создайте пару или присоединитесь по коду")
    couple = db.get(Couple, member.couple_id)
    if not couple:
        raise HTTPException(status_code=404, detail="Пространство пары не найдено")
    return couple


@app.get("/")
def root():
    return {"name": "DUO API", "docs": "/docs", "health": "/api/health"}


@app.get("/api/health")
def health():
    return {"status": "ok", "service": "duo-api", "version": "2.0.0"}


@app.get("/api/health/ready")
def readiness(db: Session = Depends(get_db)):
    try:
        db.execute(text("SELECT 1"))
        active_cities = db.scalar(select(func.count()).select_from(City).where(City.is_active.is_(True)))
    except SQLAlchemyError:
        raise HTTPException(status_code=503, detail="Database unavailable")
    return {"status": "ready", "database": "ok", "active_cities": active_cities or 0}


def require_active_city(db: Session, city_slug: str) -> City:
    city = db.get(City, city_slug)
    if not city or not city.is_active:
        raise HTTPException(status_code=404, detail="Город пока недоступен")
    return city


@app.get("/api/cities", response_model=list[CityOut])
def list_cities(db: Session = Depends(get_db)):
    return db.scalars(select(City).where(City.is_active.is_(True)).order_by(City.name)).all()


@app.get("/api/places", response_model=list[PlaceOut])
def list_places(city: str = Query(default="minsk", min_length=2, max_length=80), q: str | None = None, category: str | None = None, risk: str | None = None, max_cost: Decimal | None = Query(default=None, ge=0), limit: int = Query(default=150, ge=1, le=250), db: Session = Depends(get_db)):
    city_record = require_active_city(db, city)
    query = select(Place).where(Place.is_active.is_(True), Place.city_slug == city_record.slug)
    if q:
        pattern = f"%{q.strip()}%"
        query = query.where(or_(Place.name.ilike(pattern), Place.description.ilike(pattern), Place.address.ilike(pattern)))
    if category and category != "Все":
        query = query.where(Place.category == category)
    if risk:
        query = query.where(Place.risk == risk)
    if max_cost is not None:
        query = query.where(or_(Place.cost.is_(None), Place.cost <= max_cost))
    return db.scalars(query.order_by(Place.name).limit(limit)).all()


@app.get("/api/places/{slug}", response_model=PlaceOut)
def get_place(slug: str, city: str = Query(default="minsk", min_length=2, max_length=80), db: Session = Depends(get_db)):
    city_record = require_active_city(db, city)
    place = db.scalar(select(Place).where(Place.slug == slug, Place.city_slug == city_record.slug, Place.is_active.is_(True)))
    if not place:
        raise HTTPException(status_code=404, detail="Место не найдено")
    return place


@app.get("/api/events", response_model=list[EventOut])
def list_events(day: date | None = None, days: int = Query(default=30, ge=1, le=365), limit: int = Query(default=250, ge=1, le=500), city: str = Query(default="minsk", min_length=2, max_length=80), db: Session = Depends(get_db)):
    city_record = require_active_city(db, city)
    now = datetime.now(timezone.utc)
    query = select(DuoEvent).where(DuoEvent.city_slug == city_record.slug, DuoEvent.status == "scheduled", or_(DuoEvent.ends_at >= now, (DuoEvent.ends_at.is_(None) & (DuoEvent.starts_at >= now))))
    if day:
        start = datetime.combine(day, time.min, tzinfo=ZoneInfo(city_record.timezone))
        end = start + timedelta(days=1)
        query = query.where(DuoEvent.starts_at < end, or_(DuoEvent.ends_at.is_(None), DuoEvent.ends_at >= start))
    else:
        query = query.where(DuoEvent.starts_at < now + timedelta(days=days))
    return db.scalars(query.order_by(DuoEvent.starts_at).limit(limit)).all()


@app.get("/api/updates", response_model=list[PlaceUpdateOut])
def list_updates(limit: int = Query(default=9, ge=1, le=50), city: str = Query(default="minsk", min_length=2, max_length=80), db: Session = Depends(get_db)):
    city_record = require_active_city(db, city)
    return db.scalars(select(DuoPlaceUpdate).where(DuoPlaceUpdate.city_slug == city_record.slug).order_by(DuoPlaceUpdate.reported_on.desc()).limit(limit)).all()


@app.get("/api/me")
def me(user: AuthUser = Depends(require_user), db: Session = Depends(get_db)):
    member = db.scalar(select(CoupleMember).where(CoupleMember.user_id == user.id).limit(1))
    if not member:
        return {"id": str(user.id), "email": user.email, "couple": None}
    couple = db.get(Couple, member.couple_id)
    return {"id": str(user.id), "email": user.email, "couple": {"id": str(couple.id), "name": couple.name, "invite_code": couple.invite_code, "role": member.role}}



def _load_couple_preferences(db: Session, couple_id: UUID, user_id: UUID):
    row = db.execute(text("""
        SELECT preferences,
               ARRAY(SELECT user_id::text FROM public.couple_members WHERE couple_id = :couple) AS member_ids
        FROM public.couples
        WHERE id = :couple
    """), {"couple": couple_id}).mappings().one()
    members = (row["preferences"] or {}).get("members", {})
    active_member_ids = set(row["member_ids"] or [])
    mine = members.get(str(user_id))
    partner = next(
        (members[member_id] for member_id in active_member_ids if member_id != str(user_id) and member_id in members),
        None,
    )
    return members, mine, partner


@app.get("/api/couples/preferences")
def get_couple_preferences(user: AuthUser = Depends(require_user), db: Session = Depends(get_db)):
    """Return each partner's own discovery preferences without exposing account data."""
    couple = get_couple(db, user)
    members, mine, partner = _load_couple_preferences(db, couple.id, user.id)
    return {"mine": mine, "partner": partner}


@app.put("/api/couples/preferences")
def update_couple_preferences(payload: CouplePreferencesIn, user: AuthUser = Depends(require_user), db: Session = Depends(get_db)):
    """Persist only the authenticated member's discovery preferences."""
    couple = get_couple(db, user)
    preferences_json = json.dumps(payload.model_dump())
    db.execute(
        text("SELECT private.set_couple_member_preferences(:couple, CAST(:preferences AS jsonb))"),
        {"preferences": preferences_json, "couple": couple.id},
    )
    db.commit()
    _, _, partner = _load_couple_preferences(db, couple.id, user.id)
    return {"mine": payload.model_dump(), "partner": partner}


@app.post("/api/couples", response_model=CoupleOut, status_code=201)
def create_couple(payload: CoupleCreate, user: AuthUser = Depends(require_user), db: Session = Depends(get_db)):
    existing = db.scalar(select(CoupleMember).where(CoupleMember.user_id == user.id))
    if existing:
        raise HTTPException(status_code=409, detail="Вы уже состоите в паре")
    try:
        row = db.execute(text("select * from private.create_couple(:name)"), {"name": payload.name.strip() or "Наша пара"}).mappings().one()
        db.commit()
    except Exception as exc:
        db.rollback()
        if "couple_members_user_id_key" in str(exc) or "User already belongs to a couple" in str(exc):
            raise HTTPException(status_code=409, detail="Вы уже состоите в паре")
        raise
    return CoupleOut(id=row["id"], name=row["name"], invite_code=row["invite_code"], role="owner")


@app.post("/api/couples/join", response_model=CoupleOut)
def join_couple(payload: CoupleJoin, user: AuthUser = Depends(require_user), db: Session = Depends(get_db)):
    if db.scalar(select(CoupleMember).where(CoupleMember.user_id == user.id)):
        raise HTTPException(status_code=409, detail="Вы уже состоите в паре")
    try:
        row = db.execute(text("select * from private.join_couple(:code)"), {"code": payload.invite_code.strip().upper()}).mappings().one()
    except Exception as exc:
        db.rollback()
        message = str(exc)
        if "В паре уже два участника" in message:
            raise HTTPException(status_code=409, detail="В этой паре уже два участника")
        if "User already belongs to another couple" in message or "couple_members_user_id_key" in message:
            raise HTTPException(status_code=409, detail="Вы уже состоите в паре")
        raise HTTPException(status_code=404, detail="Код пары не найден")
    db.commit()
    return CoupleOut(id=row["id"], name=row["name"], invite_code=row["invite_code"], role="member")


@app.delete("/api/couples/me", status_code=204)
def leave_couple(user: AuthUser = Depends(require_user), db: Session = Depends(get_db)):
    """Remove the current user from their shared couple space without affecting a remaining member."""
    member = db.scalar(select(CoupleMember).where(CoupleMember.user_id == user.id).limit(1))
    if not member:
        raise HTTPException(status_code=404, detail="Вы не состоите в паре")
    db.execute(delete(CoupleMember).where(CoupleMember.user_id == user.id, CoupleMember.couple_id == member.couple_id))
    db.commit()
    return None


@app.get("/api/activity")
def get_activity(user: AuthUser = Depends(require_user), db: Session = Depends(get_db)):
    member = db.scalar(select(CoupleMember).where(CoupleMember.user_id == user.id).limit(1))
    rows = db.scalars(select(PlaceActivity).where(PlaceActivity.couple_id == member.couple_id)).all() if member else db.scalars(select(PersonalPlaceActivity).where(PersonalPlaceActivity.user_id == user.id)).all()
    return [{"place_slug": r.place_slug, "place_name": r.place_name, "is_favorite": r.is_favorite, "visited_at": r.visited_at, "rating": r.rating, "note": r.note} for r in rows]




def _recommendation_category(value: str | None) -> str:
    category = (value or "").lower()
    if any(word in category for word in ("ресторан", "ужин")):
        return "Рестораны"
    if any(word in category for word in ("кофейн", "кофе", "завтрак")):
        return "Кофейни"
    if any(word in category for word in ("бар", "паб", "винн", "коктейл", "тики")):
        return "Бары и пабы"
    if any(word in category for word in ("музе", "театр", "кино", "выстав", "арт", "культур", "наука", "музык", "галере")):
        return "Культура"
    if any(word in category for word in ("прогул", "природ", "парк", "видов")):
        return "Прогулки и отдых"
    if any(word in category for word in ("игр", "квест", "vr", "экстрим", "спорт", "скал", "картинг", "вода", "лёд", "лед", "актив", "танц", "полёт", "полет", "скорост", "spa")):
        return "Активности"
    return "Другое"


@app.post("/api/recommendations")
def get_recommendations(payload: RecommendationRequest, user: AuthUser = Depends(require_user), db: Session = Depends(get_db)):
    """Rank active places using the current user's preferences and real activity signals."""
    city = require_active_city(db, payload.city_slug)
    member = db.scalar(select(CoupleMember).where(CoupleMember.user_id == user.id).limit(1))
    is_couple = bool(member)
    if member:
        couple = db.get(Couple, member.couple_id)
        if not couple:
            raise HTTPException(status_code=404, detail="Пространство пары не найдено")
        _, stored_own_preferences, stored_partner_preferences = _load_couple_preferences(db, couple.id, user.id)
        own_preferences = stored_own_preferences or {
            "interests": payload.interests,
            "avoid": payload.avoid,
        }
        partner_preferences = stored_partner_preferences or {}
        preference_sets = [own_preferences, partner_preferences]
        activities = db.scalars(
            select(PlaceActivity).where(PlaceActivity.couple_id == member.couple_id)
        ).all()
        mutual_likes = set(db.execute(text("""
            SELECT v.place_slug
            FROM public.duo_match_votes v
            JOIN public.duo_match_sessions s ON s.id = v.session_id
            WHERE s.couple_id = :couple AND v.liked IS TRUE
            GROUP BY v.session_id, v.place_slug
            HAVING COUNT(DISTINCT v.user_id) >= 2
        """), {"couple": couple.id}).scalars().all())
    else:
        preference_sets = [{"interests": payload.interests, "avoid": payload.avoid}]
        activities = db.scalars(
            select(PersonalPlaceActivity).where(PersonalPlaceActivity.user_id == user.id)
        ).all()
        mutual_likes = set()

    interests_by_member = [
        {_recommendation_category(item) for item in prefs.get("interests", [])}
        for prefs in preference_sets
    ]
    avoided = {
        _recommendation_category(item)
        for prefs in preference_sets
        for item in prefs.get("avoid", [])
    }
    activity_by_slug = {item.place_slug: item for item in activities}
    places = db.scalars(
        select(Place).where(Place.city_slug == city.slug, Place.is_active.is_(True))
    ).all()
    dismissed_slugs = set(db.scalars(select(RecommendationFeedback.place_slug).where(RecommendationFeedback.user_id == user.id)).all())
    places_by_slug = {place.slug: place for place in places}
    liked_categories = set()
    disliked_categories = set()
    for item in activities:
        related_place = places_by_slug.get(item.place_slug)
        if not related_place:
            continue
        related_category = _recommendation_category(related_place.category)
        if item.is_favorite or (item.rating is not None and item.rating >= 4):
            liked_categories.add(related_category)
        elif item.rating is not None and item.rating <= 2:
            disliked_categories.add(related_category)

    ranked = []
    for place in places:
        category = _recommendation_category(place.category)
        activity = activity_by_slug.get(place.slug)
        if place.slug in dismissed_slugs or category in avoided or place.risk == "avoid" or place.level > 3 or (activity and (activity.is_favorite or activity.visited_at)):
            continue
        score = 0
        reasons = []
        matched_members = sum(category in interests for interests in interests_by_member)
        if matched_members == 2:
            score += 30
            reasons.append("Интересно обоим")
        elif matched_members == 1:
            score += 17
            reasons.append("Совпадает с вашими интересами")

        if category in liked_categories:
            score += 12
            reasons.append("Вам нравятся места этой категории")
        elif category in disliked_categories:
            score -= 10
        if place.slug in mutual_likes:
            score += 18
            reasons.append("Вы оба выбрали это в DUO Match")

        try:
            external_rating = float(str(place.rating).replace(",", "."))
        except (TypeError, ValueError):
            external_rating = 0
        if 0 < external_rating <= 5:
            score += round(external_rating * 3)
            if external_rating >= 4.5:
                reasons.append("Высокая оценка гостей")
        score += 4

        if not reasons:
            reasons.append("Идея для нового открытия")
        ranked.append((score, place, reasons[:3]))

    ranked.sort(key=lambda item: (-item[0], item[1].name.casefold(), item[1].slug))
    return {
        "items": [
            {
                **PlaceOut.model_validate(place).model_dump(),
                "score": score,
                "reasons": reasons,
            }
            for score, place, reasons in ranked[:payload.limit]
        ],
        "context": {
            "is_couple": is_couple,
            "uses_preferences": any(interests_by_member) or bool(avoided),
            "signals": ["интересы", "избранное", "оценки", "посещения"] + (["DUO Match"] if is_couple else []),
        },
    }



@app.post("/api/recommendations/{place_slug}/dismiss", status_code=204)
def dismiss_recommendation(place_slug: str, user: AuthUser = Depends(require_user), db: Session = Depends(get_db)):
    """Hide a recommendation only for the authenticated user."""
    place_exists = db.scalar(select(Place.slug).where(Place.slug == place_slug, Place.is_active.is_(True)))
    if not place_exists:
        raise HTTPException(status_code=404, detail="Место не найдено")
    db.execute(
        insert(RecommendationFeedback)
        .values(user_id=user.id, place_slug=place_slug, action="dismiss")
        .on_conflict_do_nothing(index_elements=["user_id", "place_slug"])
    )
    db.commit()
    return None


@app.delete("/api/recommendations/{place_slug}/dismiss")
def restore_recommendation(place_slug: str, user: AuthUser = Depends(require_user), db: Session = Depends(get_db)):
    """Restore a recommendation previously hidden by the authenticated user."""
    db.execute(delete(RecommendationFeedback).where(
        RecommendationFeedback.user_id == user.id,
        RecommendationFeedback.place_slug == place_slug,
    ))
    db.commit()
    return {"status": "restored"}


@app.get("/api/analytics/couple")
def get_couple_analytics(user: AuthUser = Depends(require_user), db: Session = Depends(get_db)):
    """Return shared activity and DUO Match aggregates for the authenticated user's couple."""
    couple = get_couple(db, user)
    activity = db.execute(text("""
        SELECT COUNT(*) FILTER (WHERE is_favorite)::int AS favorites,
               COUNT(*) FILTER (WHERE visited_at IS NOT NULL)::int AS visits,
               COUNT(*) FILTER (WHERE rating IS NOT NULL)::int AS ratings,
               COALESCE(ROUND(AVG(rating)::numeric, 1), 0)::float AS average_rating
        FROM public.place_activity
        WHERE couple_id = :couple
    """), {"couple": couple.id}).mappings().one()
    categories = db.execute(text("""
        SELECT p.category AS name,
               COUNT(*)::int AS value
        FROM public.place_activity a
        JOIN public.places p ON p.slug = a.place_slug
        WHERE a.couple_id = :couple
          AND (a.is_favorite IS TRUE OR a.visited_at IS NOT NULL)
        GROUP BY p.category
        ORDER BY value DESC, p.category
        LIMIT 6
    """), {"couple": couple.id}).mappings().all()
    match_stats = db.execute(text("""
        SELECT COUNT(*)::int AS rounds,
               COUNT(*) FILTER (WHERE status = 'completed')::int AS completed_rounds,
               COALESCE(SUM(mutual_matches), 0)::int AS mutual_matches
        FROM (
            SELECT s.id, s.status, COUNT(m.place_slug)::int AS mutual_matches
            FROM public.duo_match_sessions s
            LEFT JOIN (
                SELECT session_id, place_slug
                FROM public.duo_match_votes
                WHERE liked IS TRUE
                GROUP BY session_id, place_slug
                HAVING COUNT(DISTINCT user_id) >= 2
            ) m ON m.session_id = s.id
            WHERE s.couple_id = :couple
            GROUP BY s.id, s.status
        ) rounds
    """), {"couple": couple.id}).mappings().one()
    history = db.execute(text("""
        SELECT s.id::text AS id, s.status, s.city_slug, s.created_at,
               COUNT(m.place_slug)::int AS mutual_matches
        FROM public.duo_match_sessions s
        LEFT JOIN (
            SELECT session_id, place_slug
            FROM public.duo_match_votes
            WHERE liked IS TRUE
            GROUP BY session_id, place_slug
            HAVING COUNT(DISTINCT user_id) >= 2
        ) m ON m.session_id = s.id
        WHERE s.couple_id = :couple
        GROUP BY s.id
        ORDER BY s.created_at DESC
        LIMIT 5
    """), {"couple": couple.id}).mappings().all()
    return {
        "activity": dict(activity),
        "common_interests": [dict(row) for row in categories],
        "match_stats": dict(match_stats),
        "match_history": [dict(row) for row in history],
    }


@app.put("/api/activity", status_code=204)
def sync_activity(items: list[ActivitySyncItem], user: AuthUser = Depends(require_user), db: Session = Depends(get_db)):
    place_slugs = [item.place_slug for item in items]
    if len(place_slugs) != len(set(place_slugs)):
        raise HTTPException(status_code=422, detail="В запросе не должно быть повторяющихся мест")
    member = db.scalar(select(CoupleMember).where(CoupleMember.user_id == user.id).limit(1))
    slugs = [item.place_slug for item in items]
    places = db.scalars(select(Place).where(Place.slug.in_(slugs))).all() if slugs else []
    names = {p.slug: p.name for p in places}
    now = datetime.now(timezone.utc)
    for item in items:
        place_name = names.get(item.place_slug)
        if not place_name:
            continue
        changes = item.model_dump(exclude_unset=True, exclude={"place_slug"})
        values = {
            "id": uuid4(),
            "place_slug": item.place_slug,
            "place_name": place_name,
            "is_favorite": changes.get("is_favorite", False),
            "visited_at": now if changes.get("visited") is True else None,
            "rating": changes.get("rating"),
            "note": changes.get("note", ""),
            "updated_at": now,
        }
        update_values = {"updated_at": now}
        for field, value in changes.items():
            column = "visited_at" if field == "visited" else field
            update_values[column] = (now if value else None) if field == "visited" else value
        if member:
            values.update({"couple_id": member.couple_id, "updated_by": user.id})
            update_values["updated_by"] = user.id
            stmt = insert(PlaceActivity).values(**values).on_conflict_do_update(
                constraint="place_activity_couple_id_place_slug_key",
                set_=update_values,
            )
        else:
            values["user_id"] = user.id
            stmt = insert(PersonalPlaceActivity).values(**values).on_conflict_do_update(
                constraint="personal_place_activity_user_place_key",
                set_=update_values,
            )
        db.execute(stmt)
    db.commit()
    return None


@app.get("/api/plans", response_model=list[PlanOut])
def list_plans(user: AuthUser = Depends(require_user), db: Session = Depends(get_db)):
    couple = get_couple(db, user)
    return db.scalars(select(DuoDatePlan).where(DuoDatePlan.couple_id == couple.id).order_by((DuoDatePlan.plan_date < date.today()).asc(), DuoDatePlan.plan_date.asc(), DuoDatePlan.created_at.desc()).limit(50)).all()


@app.post("/api/plans", response_model=PlanOut, status_code=201)
def create_plan(payload: PlanCreate, user: AuthUser = Depends(require_user), db: Session = Depends(get_db)):
    couple = get_couple(db, user)
    now = datetime.now(timezone.utc)
    plan = DuoDatePlan(id=uuid4(), couple_id=couple.id, created_by=user.id, updated_by=user.id, plan_date=payload.plan_date, title=payload.title, mood=payload.mood, budget=payload.budget, items=payload.items, notes=payload.notes, created_at=now, updated_at=now)
    db.add(plan)
    db.flush()
    db.refresh(plan)
    db.commit()
    return plan


@app.patch("/api/plans/{plan_id}", response_model=PlanOut)
def update_plan(plan_id: UUID, payload: PlanUpdate, user: AuthUser = Depends(require_user), db: Session = Depends(get_db)):
    """Update a saved itinerary shared by the authenticated couple."""
    couple = get_couple(db, user)
    # Lock the row so two partners cannot pass the version check concurrently.
    plan = db.scalar(select(DuoDatePlan).where(
        DuoDatePlan.id == plan_id, DuoDatePlan.couple_id == couple.id
    ).with_for_update())
    if not plan:
        raise HTTPException(status_code=404, detail="План не найден")
    changes = payload.model_dump(exclude_unset=True)
    expected_updated_at = changes.pop("expected_updated_at", None)
    if expected_updated_at is None:
        raise HTTPException(status_code=422, detail="Не передана версия плана. Обновите страницу и повторите попытку.")
    if not changes:
        raise HTTPException(status_code=422, detail="Нет изменений для сохранения")
    if any(value is None for value in changes.values()):
        raise HTTPException(status_code=422, detail="Поля плана не могут быть пустыми")
    if expected_updated_at is not None and expected_updated_at != plan.updated_at:
        raise HTTPException(
            status_code=409,
            detail="План уже изменён другим участником. Обновите данные и повторите изменения.",
        )
    for field, value in changes.items():
        setattr(plan, field, value)
    plan.updated_by = user.id
    plan.updated_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(plan)
    return plan


@app.delete("/api/plans/{plan_id}", status_code=204)
def delete_plan(
    plan_id: UUID,
    expected_updated_at: datetime,
    user: AuthUser = Depends(require_user),
    db: Session = Depends(get_db),
):
    """Delete a shared plan only when the client holds its latest version."""
    couple = get_couple(db, user)
    plan = db.scalar(select(DuoDatePlan).where(
        DuoDatePlan.id == plan_id,
        DuoDatePlan.couple_id == couple.id,
    ).with_for_update())
    if not plan:
        raise HTTPException(status_code=404, detail="План не найден")
    if expected_updated_at != plan.updated_at:
        raise HTTPException(
            status_code=409,
            detail="План уже изменён другим участником. Обновите данные и повторите удаление.",
        )
    db.delete(plan)
    db.commit()
    return None



@app.post("/api/match/sessions", status_code=201)
def create_match_session(payload: MatchSessionCreate, user: AuthUser = Depends(require_match_user), db: Session = Depends(get_db)):
    couple = get_couple(db, user)
    member_count = db.scalar(select(func.count()).select_from(CoupleMember).where(CoupleMember.couple_id == couple.id)) or 0
    if member_count < 2:
        raise HTTPException(status_code=409, detail="Пригласите второго участника в пространство пары, чтобы начать совместный выбор")
    city = require_active_city(db, payload.city_slug)
    active_session = db.execute(text("""SELECT s.id, s.status, s.city_slug,
        (SELECT count(*) FROM public.duo_match_candidates c WHERE c.session_id=s.id) AS candidate_count
        FROM public.duo_match_sessions s WHERE s.couple_id=:couple AND s.city_slug=:city AND s.status='active'
        ORDER BY s.created_at DESC LIMIT 1"""), {"couple": couple.id, "city": city.slug}).mappings().first()
    if active_session:
        return {"id": str(active_session["id"]), "status": active_session["status"],
                "candidate_count": active_session["candidate_count"], "city_slug": active_session["city_slug"],
                "resumed": True}
    query = "SELECT slug FROM public.places WHERE city_slug = :city AND is_active IS TRUE"
    params = {"city": city.slug, "limit": payload.limit}
    if payload.category:
        query += " AND category = :category"
        params["category"] = payload.category
    query += " ORDER BY random() LIMIT :limit"
    slugs = db.execute(text(query), params).scalars().all()
    if len(slugs) < 2:
        raise HTTPException(status_code=422, detail="Недостаточно мест для совместного выбора")
    session_id = uuid4()
    db.execute(text("INSERT INTO public.duo_match_sessions (id, couple_id, city_slug, created_by) VALUES (:id, :couple, :city, :user)"), {"id": session_id, "couple": couple.id, "city": city.slug, "user": user.id})
    for position, slug in enumerate(slugs):
        db.execute(text("INSERT INTO public.duo_match_candidates (session_id, place_slug, position) VALUES (:session, :slug, :position)"), {"session": session_id, "slug": slug, "position": position})
    db.commit()
    return {"id": str(session_id), "status": "active", "candidate_count": len(slugs), "city_slug": city.slug, "resumed": False}


def _match_session_payload(session_id: UUID, user: AuthUser, couple: Couple, db: Session):
    session_row = db.execute(text("SELECT id, status, city_slug, created_at FROM public.duo_match_sessions WHERE id = :id AND couple_id = :couple"), {"id": session_id, "couple": couple.id}).mappings().first()
    if not session_row:
        raise HTTPException(status_code=404, detail="Раунд DUO Match не найден")
    rows = db.execute(text("""
        SELECT p.slug, p.name, p.category, p.description, p.address, p.rating, p.reviews, p.price_label, p.image_url, p.image_source_url, p.latitude, p.longitude, p.district, c.position,
               bool_or(v.liked) FILTER (WHERE v.user_id = :user_id) AS my_vote,
               CASE
                   WHEN bool_or(v.liked) FILTER (WHERE v.user_id = :user_id) IS TRUE
                    AND bool_or(v.liked) FILTER (WHERE v.user_id <> :user_id) IS TRUE
                   THEN TRUE
                   ELSE NULL
               END AS partner_vote,
               count(v.user_id) FILTER (WHERE v.user_id <> :user_id) > 0 AS partner_has_voted
        FROM public.duo_match_candidates c
        JOIN public.places p ON p.slug = c.place_slug
        LEFT JOIN public.duo_match_votes v ON v.session_id = c.session_id AND v.place_slug = c.place_slug
        WHERE c.session_id = :session_id
        GROUP BY p.slug, c.position
        ORDER BY c.position
    """), {"user_id": user.id, "session_id": session_id}).mappings().all()
    candidates = [dict(row) for row in rows]
    return {"session": dict(session_row), "candidates": candidates, "matches": [r for r in candidates if r["my_vote"] is True and r["partner_vote"] is True], "my_votes": sum(r["my_vote"] is not None for r in candidates), "partner_votes": sum(bool(r["partner_has_voted"]) for r in candidates), "candidate_count": len(candidates)}


@app.get("/api/match/sessions/active")
def get_active_match_session(city_slug: str = Query(..., min_length=2, max_length=80), user: AuthUser = Depends(require_match_user), db: Session = Depends(get_db)):
    couple = get_couple(db, user)
    city = require_active_city(db, city_slug)
    active_session = db.execute(text("""SELECT id, status, city_slug
        FROM public.duo_match_sessions
        WHERE couple_id = :couple AND city_slug = :city AND status = 'active'
        ORDER BY created_at DESC LIMIT 1"""), {"couple": couple.id, "city": city.slug}).mappings().first()
    if not active_session:
        return {"active": False}
    return {"active": True, "id": str(active_session["id"]), "status": active_session["status"],
            "city_slug": active_session["city_slug"]}


@app.get("/api/match/sessions/{session_id}")
def get_match_session(session_id: UUID, user: AuthUser = Depends(require_match_user), db: Session = Depends(get_db)):
    couple = get_couple(db, user)
    return _match_session_payload(session_id, user, couple, db)


@app.put("/api/match/sessions/{session_id}/votes")
def vote_match_candidate(session_id: UUID, payload: MatchVoteIn, user: AuthUser = Depends(require_match_user), db: Session = Depends(get_db)):
    couple = get_couple(db, user)
    exists = db.execute(text("SELECT 1 FROM public.duo_match_sessions s JOIN public.duo_match_candidates c ON c.session_id=s.id WHERE s.id=:session AND s.couple_id=:couple AND c.place_slug=:slug"), {"session": session_id, "couple": couple.id, "slug": payload.place_slug}).first()
    if not exists:
        raise HTTPException(status_code=404, detail="Место не входит в этот раунд")
    db.execute(text("""INSERT INTO public.duo_match_votes (session_id, place_slug, user_id, liked) VALUES (:session, :slug, :user, :liked)
        ON CONFLICT (session_id, place_slug, user_id) DO UPDATE SET liked=EXCLUDED.liked, updated_at=now()"""), {"session": session_id, "slug": payload.place_slug, "user": user.id, "liked": payload.liked})
    # Publish a safe session-row update. Vote values stay private to the API response.
    db.execute(text("""UPDATE public.duo_match_sessions
        SET activity_version = activity_version + 1
        WHERE id = :session AND couple_id = :couple"""), {"session": session_id, "couple": couple.id})
    db.execute(text("""UPDATE public.duo_match_sessions s SET status='completed'
        WHERE s.id=:session AND (SELECT count(*) FROM public.duo_match_votes v WHERE v.session_id=s.id) =
          2 * (SELECT count(*) FROM public.duo_match_candidates c WHERE c.session_id=s.id)
        AND (SELECT count(DISTINCT user_id) FROM public.duo_match_votes v WHERE v.session_id=s.id) >= 2"""), {"session": session_id})
    result = _match_session_payload(session_id, user, couple, db)
    db.commit()
    return result
