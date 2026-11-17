import uuid
from datetime import date, datetime
from decimal import Decimal
from sqlalchemy import Boolean, Date, DateTime, ForeignKey, Integer, Numeric, SmallInteger, String, Text, UniqueConstraint, func
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column
from app.database import Base


class City(Base):
    __tablename__ = "cities"
    __table_args__ = {"schema": "public"}
    slug: Mapped[str] = mapped_column(String(80), primary_key=True)
    name: Mapped[str] = mapped_column(String(120))
    name_localized: Mapped[str] = mapped_column(Text)
    country_code: Mapped[str] = mapped_column(String(2))
    country_name: Mapped[str] = mapped_column(String(120))
    country_name_localized: Mapped[str] = mapped_column(Text)
    timezone: Mapped[str] = mapped_column(String(80))
    currency_code: Mapped[str] = mapped_column(String(3))
    default_language: Mapped[str] = mapped_column(String(8))
    is_active: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())


class Place(Base):
    __tablename__ = "places"
    __table_args__ = {"schema": "public"}
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    city_slug: Mapped[str] = mapped_column(String(80), ForeignKey("public.cities.slug"), default="minsk", server_default="minsk")
    slug: Mapped[str] = mapped_column(String(180), unique=True)
    name: Mapped[str] = mapped_column(String(255), index=True)
    category: Mapped[str] = mapped_column(String(120), index=True)
    emoji: Mapped[str] = mapped_column(String(16), default="✨")
    description: Mapped[str] = mapped_column(Text, default="")
    address: Mapped[str] = mapped_column(Text, default="")
    rating: Mapped[str] = mapped_column(String(32), default="—")
    reviews: Mapped[str] = mapped_column(String(32), default="—")
    price_label: Mapped[str] = mapped_column(Text, default="")
    couple_price_label: Mapped[str] = mapped_column(Text, default="")
    level: Mapped[int] = mapped_column(SmallInteger, default=1)
    risk: Mapped[str] = mapped_column(String(24), default="good")
    tip: Mapped[str] = mapped_column(Text, default="")
    website_url: Mapped[str] = mapped_column(Text, default="")
    source_name: Mapped[str] = mapped_column(String(120), default="")
    source_url: Mapped[str] = mapped_column(Text, default="")
    cost: Mapped[Decimal | None] = mapped_column(Numeric(10, 2), nullable=True)
    latitude: Mapped[float | None] = mapped_column(nullable=True)
    longitude: Mapped[float | None] = mapped_column(nullable=True)
    location_verified_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    district: Mapped[str | None] = mapped_column(String(120), nullable=True)
    image_url: Mapped[str | None] = mapped_column(Text, nullable=True)
    image_source_url: Mapped[str | None] = mapped_column(Text, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())


class Couple(Base):
    __tablename__ = "couples"
    __table_args__ = {"schema": "public"}
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True)
    name: Mapped[str] = mapped_column(Text)
    invite_code: Mapped[str] = mapped_column(Text, unique=True)
    created_by: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))


class CoupleMember(Base):
    __tablename__ = "couple_members"
    __table_args__ = {"schema": "public"}
    couple_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True)
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True)
    role: Mapped[str] = mapped_column(Text, default="member")
    joined_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))


class PlaceActivity(Base):
    __tablename__ = "place_activity"
    __table_args__ = (UniqueConstraint("couple_id", "place_slug", name="place_activity_couple_id_place_slug_key"), {"schema": "public"})
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    couple_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), index=True)
    place_slug: Mapped[str] = mapped_column(String(180), ForeignKey("public.places.slug", ondelete="CASCADE"))
    place_name: Mapped[str] = mapped_column(Text)
    is_favorite: Mapped[bool] = mapped_column(Boolean, default=False)
    visited_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    rating: Mapped[int | None] = mapped_column(SmallInteger, nullable=True)
    note: Mapped[str] = mapped_column(Text, default="")
    updated_by: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True))
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))


class PersonalPlaceActivity(Base):
    __tablename__ = "personal_place_activity"
    __table_args__ = (UniqueConstraint("user_id", "place_slug", name="personal_place_activity_user_place_key"), {"schema": "public"})
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), index=True)
    place_slug: Mapped[str] = mapped_column(String(180), ForeignKey("public.places.slug", ondelete="CASCADE"))
    place_name: Mapped[str] = mapped_column(Text)
    is_favorite: Mapped[bool] = mapped_column(Boolean, default=False)
    visited_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    rating: Mapped[int | None] = mapped_column(SmallInteger, nullable=True)
    note: Mapped[str] = mapped_column(Text, default="")
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))


class DuoEvent(Base):
    __tablename__ = "duo_events"
    __table_args__ = {"schema": "public"}
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True)
    city_slug: Mapped[str] = mapped_column(String(80), ForeignKey("public.cities.slug"), default="minsk", server_default="minsk")
    source_key: Mapped[str] = mapped_column(Text)
    source_url: Mapped[str] = mapped_column(Text)
    title: Mapped[str] = mapped_column(Text)
    description: Mapped[str] = mapped_column(Text)
    category: Mapped[str] = mapped_column(Text)
    venue: Mapped[str] = mapped_column(Text)
    address: Mapped[str] = mapped_column(Text)
    starts_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    ends_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    price_min: Mapped[Decimal | None] = mapped_column(Numeric(10, 2), nullable=True)
    price_max: Mapped[Decimal | None] = mapped_column(Numeric(10, 2), nullable=True)
    currency: Mapped[str] = mapped_column(Text)
    image_url: Mapped[str | None] = mapped_column(Text, nullable=True)
    ticket_url: Mapped[str | None] = mapped_column(Text, nullable=True)
    status: Mapped[str] = mapped_column(Text)
    last_verified_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))


class DuoDatePlan(Base):
    __tablename__ = "duo_date_plans"
    __table_args__ = {"schema": "public"}
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True)
    couple_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), index=True)
    created_by: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True))
    plan_date: Mapped[date] = mapped_column(Date)
    title: Mapped[str] = mapped_column(Text)
    mood: Mapped[str] = mapped_column(Text)
    budget: Mapped[Decimal] = mapped_column(Numeric(10, 2))
    items: Mapped[list] = mapped_column(JSONB)
    notes: Mapped[str] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))


class DuoPlaceUpdate(Base):
    __tablename__ = "duo_place_updates"
    __table_args__ = {"schema": "public"}
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True)
    city_slug: Mapped[str] = mapped_column(String(80), ForeignKey("public.cities.slug"), default="minsk", server_default="minsk")
    place_name: Mapped[str] = mapped_column(Text)
    change_type: Mapped[str] = mapped_column(Text)
    address: Mapped[str] = mapped_column(Text)
    description: Mapped[str] = mapped_column(Text)
    reported_on: Mapped[date] = mapped_column(Date)
    source_name: Mapped[str] = mapped_column(Text)
    source_url: Mapped[str] = mapped_column(Text)
    verified_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
