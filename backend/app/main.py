from contextlib import asynccontextmanager
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
from app.auth import AuthUser, require_user
from app.models.entities import City, Place, Couple, CoupleMember, PlaceActivity, PersonalPlaceActivity, DuoEvent, DuoDatePlan, DuoPlaceUpdate
from app.schemas import CityOut, PlaceOut, EventOut, PlaceUpdateOut, CoupleCreate, CoupleJoin, CoupleOut, ActivitySyncItem, PlanCreate, PlanOut, MatchSessionCreate, MatchVoteIn

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Schema is managed by Alembic migrations; never create tables at runtime.
    yield


app = FastAPI(title="DUO API", version="2.0.0", description="Backend для DUO — city discovery and shared date planning", lifespan=lifespan)
app.add_middleware(CORSMiddleware, allow_origins=settings.allowed_origins, allow_credentials=True, allow_methods=["*"], allow_headers=["*"])


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
    member = db.scalar(select(CoupleMember).where(CoupleMember.user_id == user.id).limit(1))
    slugs = [item.place_slug for item in items]
    places = db.scalars(select(Place).where(Place.slug.in_(slugs))).all() if slugs else []
    names = {p.slug: p.name for p in places}
    now = datetime.now(timezone.utc)
    for item in items:
        place_name = names.get(item.place_slug)
        if not place_name:
            continue
        if member:
            stmt = insert(PlaceActivity).values(id=uuid4(), couple_id=member.couple_id, place_slug=item.place_slug, place_name=place_name, is_favorite=item.is_favorite, visited_at=now if item.visited else None, rating=item.rating, note=item.note, updated_by=user.id, updated_at=now).on_conflict_do_update(
                constraint="place_activity_couple_id_place_slug_key",
                set_={"is_favorite": item.is_favorite, "visited_at": now if item.visited else None, "rating": item.rating, "note": item.note, "updated_by": user.id, "updated_at": now},
            )
        else:
            stmt = insert(PersonalPlaceActivity).values(id=uuid4(), user_id=user.id, place_slug=item.place_slug, place_name=place_name, is_favorite=item.is_favorite, visited_at=now if item.visited else None, rating=item.rating, note=item.note, updated_at=now).on_conflict_do_update(
                constraint="personal_place_activity_user_place_key",
                set_={"is_favorite": item.is_favorite, "visited_at": now if item.visited else None, "rating": item.rating, "note": item.note, "updated_at": now},
            )
        db.execute(stmt)
    db.commit()
    return None


@app.get("/api/plans", response_model=list[PlanOut])
def list_plans(user: AuthUser = Depends(require_user), db: Session = Depends(get_db)):
    couple = get_couple(db, user)
    return db.scalars(select(DuoDatePlan).where(DuoDatePlan.couple_id == couple.id).order_by(DuoDatePlan.plan_date.asc()).limit(50)).all()


@app.post("/api/plans", response_model=PlanOut, status_code=201)
def create_plan(payload: PlanCreate, user: AuthUser = Depends(require_user), db: Session = Depends(get_db)):
    couple = get_couple(db, user)
    now = datetime.now(timezone.utc)
    plan = DuoDatePlan(id=uuid4(), couple_id=couple.id, created_by=user.id, plan_date=payload.plan_date, title=payload.title, mood=payload.mood, budget=payload.budget, items=payload.items, notes=payload.notes, created_at=now, updated_at=now)
    db.add(plan)
    db.flush()
    db.refresh(plan)
    db.commit()
    return plan


@app.delete("/api/plans/{plan_id}", status_code=204)
def delete_plan(plan_id: UUID, user: AuthUser = Depends(require_user), db: Session = Depends(get_db)):
    couple = get_couple(db, user)
    plan = db.scalar(select(DuoDatePlan).where(DuoDatePlan.id == plan_id, DuoDatePlan.couple_id == couple.id))
    if not plan:
        raise HTTPException(status_code=404, detail="План не найден")
    db.delete(plan)
    db.commit()
    return None



@app.post("/api/match/sessions", status_code=201)
def create_match_session(payload: MatchSessionCreate, user: AuthUser = Depends(require_user), db: Session = Depends(get_db)):
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
def get_active_match_session(city_slug: str = Query(..., min_length=2, max_length=80), user: AuthUser = Depends(require_user), db: Session = Depends(get_db)):
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
def get_match_session(session_id: UUID, user: AuthUser = Depends(require_user), db: Session = Depends(get_db)):
    couple = get_couple(db, user)
    return _match_session_payload(session_id, user, couple, db)


@app.put("/api/match/sessions/{session_id}/votes")
def vote_match_candidate(session_id: UUID, payload: MatchVoteIn, user: AuthUser = Depends(require_user), db: Session = Depends(get_db)):
    couple = get_couple(db, user)
    exists = db.execute(text("SELECT 1 FROM public.duo_match_sessions s JOIN public.duo_match_candidates c ON c.session_id=s.id WHERE s.id=:session AND s.couple_id=:couple AND c.place_slug=:slug"), {"session": session_id, "couple": couple.id, "slug": payload.place_slug}).first()
    if not exists:
        raise HTTPException(status_code=404, detail="Место не входит в этот раунд")
    db.execute(text("""INSERT INTO public.duo_match_votes (session_id, place_slug, user_id, liked) VALUES (:session, :slug, :user, :liked)
        ON CONFLICT (session_id, place_slug, user_id) DO UPDATE SET liked=EXCLUDED.liked, updated_at=now()"""), {"session": session_id, "slug": payload.place_slug, "user": user.id, "liked": payload.liked})
    db.execute(text("""UPDATE public.duo_match_sessions s SET status='completed'
        WHERE s.id=:session AND (SELECT count(*) FROM public.duo_match_votes v WHERE v.session_id=s.id) =
          2 * (SELECT count(*) FROM public.duo_match_candidates c WHERE c.session_id=s.id)
        AND (SELECT count(DISTINCT user_id) FROM public.duo_match_votes v WHERE v.session_id=s.id) >= 2"""), {"session": session_id})
    result = _match_session_payload(session_id, user, couple, db)
    db.commit()
    return result
