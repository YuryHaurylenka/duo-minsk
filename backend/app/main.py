from contextlib import asynccontextmanager
from datetime import date, datetime, time, timedelta, timezone
from zoneinfo import ZoneInfo
from decimal import Decimal
from uuid import UUID, uuid4
from fastapi import FastAPI, Depends, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import select, func, or_, text
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.orm import Session
from app.config import get_settings
from app.database import get_db
from app.auth import AuthUser, require_user
from app.models.entities import Place, Couple, CoupleMember, PlaceActivity, DuoEvent, DuoDatePlan, DuoPlaceUpdate
from app.schemas import PlaceOut, EventOut, PlaceUpdateOut, CoupleCreate, CoupleJoin, CoupleOut, ActivitySyncItem, PlanCreate, PlanOut

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Schema is managed by Alembic migrations; never create tables at runtime.
    yield


app = FastAPI(title="DUO API", version="2.0.0", description="Backend для DUO — свидания и места Минска", lifespan=lifespan)
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


@app.get("/api/places", response_model=list[PlaceOut])
def list_places(q: str | None = None, category: str | None = None, risk: str | None = None, max_cost: Decimal | None = Query(default=None, ge=0), limit: int = Query(default=150, ge=1, le=250), db: Session = Depends(get_db)):
    query = select(Place).where(Place.is_active.is_(True))
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
def get_place(slug: str, db: Session = Depends(get_db)):
    place = db.scalar(select(Place).where(Place.slug == slug, Place.is_active.is_(True)))
    if not place:
        raise HTTPException(status_code=404, detail="Место не найдено")
    return place


@app.get("/api/events", response_model=list[EventOut])
def list_events(day: date | None = None, days: int = Query(default=30, ge=1, le=365), limit: int = Query(default=250, ge=1, le=500), db: Session = Depends(get_db)):
    now = datetime.now(timezone.utc)
    query = select(DuoEvent).where(DuoEvent.status == "scheduled", or_(DuoEvent.ends_at >= now, (DuoEvent.ends_at.is_(None) & (DuoEvent.starts_at >= now))))
    if day:
        start = datetime.combine(day, time.min, tzinfo=ZoneInfo("Europe/Minsk"))
        end = start + timedelta(days=1)
        query = query.where(DuoEvent.starts_at < end, or_(DuoEvent.ends_at.is_(None), DuoEvent.ends_at >= start))
    else:
        query = query.where(DuoEvent.starts_at < now + timedelta(days=days))
    return db.scalars(query.order_by(DuoEvent.starts_at).limit(limit)).all()


@app.get("/api/updates", response_model=list[PlaceUpdateOut])
def list_updates(limit: int = Query(default=9, ge=1, le=50), db: Session = Depends(get_db)):
    return db.scalars(select(DuoPlaceUpdate).order_by(DuoPlaceUpdate.reported_on.desc()).limit(limit)).all()


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
    row = db.execute(text("select * from public.create_couple(:name)"), {"name": payload.name.strip() or "Наша пара"}).mappings().one()
    db.commit()
    return CoupleOut(id=row["id"], name=row["name"], invite_code=row["invite_code"], role="owner")


@app.post("/api/couples/join", response_model=CoupleOut)
def join_couple(payload: CoupleJoin, user: AuthUser = Depends(require_user), db: Session = Depends(get_db)):
    if db.scalar(select(CoupleMember).where(CoupleMember.user_id == user.id)):
        raise HTTPException(status_code=409, detail="Вы уже состоите в паре")
    try:
        row = db.execute(text("select * from public.join_couple(:code)"), {"code": payload.invite_code.strip().upper()}).mappings().one()
    except Exception as exc:
        db.rollback()
        message = str(exc)
        if "В паре уже два участника" in message:
            raise HTTPException(status_code=409, detail="В этой паре уже два участника")
        raise HTTPException(status_code=404, detail="Код пары не найден")
    db.commit()
    return CoupleOut(id=row["id"], name=row["name"], invite_code=row["invite_code"], role="member")


@app.get("/api/activity")
def get_activity(user: AuthUser = Depends(require_user), db: Session = Depends(get_db)):
    couple = get_couple(db, user)
    rows = db.scalars(select(PlaceActivity).where(PlaceActivity.couple_id == couple.id)).all()
    return [{"place_name": r.place_name, "is_favorite": r.is_favorite, "visited_at": r.visited_at, "rating": r.rating, "note": r.note} for r in rows]


@app.put("/api/activity", status_code=204)
def sync_activity(items: list[ActivitySyncItem], user: AuthUser = Depends(require_user), db: Session = Depends(get_db)):
    couple = get_couple(db, user)
    slugs = [item.place_slug for item in items]
    places = db.scalars(select(Place).where(Place.slug.in_(slugs))).all() if slugs else []
    names = {p.slug: p.name for p in places}
    now = datetime.now(timezone.utc)
    for item in items:
        place_name = names.get(item.place_slug)
        if not place_name:
            continue
        stmt = insert(PlaceActivity).values(id=uuid4(), couple_id=couple.id, place_name=place_name, is_favorite=item.is_favorite, visited_at=now if item.visited else None, rating=item.rating, note="", updated_by=user.id, updated_at=now).on_conflict_do_update(
            constraint="place_activity_couple_id_place_name_key",
            set_={"is_favorite": item.is_favorite, "visited_at": now if item.visited else None, "rating": item.rating, "updated_by": user.id, "updated_at": now},
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

