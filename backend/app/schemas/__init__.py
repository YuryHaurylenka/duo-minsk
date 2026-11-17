from datetime import date, datetime
from decimal import Decimal
from uuid import UUID
from pydantic import BaseModel, ConfigDict, Field


class PlaceOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    slug: str
    name: str
    category: str
    emoji: str
    description: str
    address: str
    rating: str
    reviews: str
    price_label: str
    couple_price_label: str
    level: int
    risk: str
    tip: str
    website_url: str
    source_name: str
    source_url: str
    cost: Decimal | None


class EventOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    title: str
    description: str
    category: str
    venue: str
    address: str
    starts_at: datetime
    ends_at: datetime | None
    price_min: Decimal | None
    price_max: Decimal | None
    currency: str
    image_url: str | None
    ticket_url: str | None
    source_url: str
    status: str
    last_verified_at: datetime


class PlaceUpdateOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    place_name: str
    change_type: str
    address: str
    description: str
    reported_on: date
    source_name: str
    source_url: str
    verified_at: datetime


class CoupleCreate(BaseModel):
    name: str = Field(default="Наша пара", min_length=1, max_length=48)


class CoupleJoin(BaseModel):
    invite_code: str = Field(min_length=6, max_length=12)


class CoupleOut(BaseModel):
    id: UUID
    name: str
    invite_code: str
    role: str


class ActivitySyncItem(BaseModel):
    place_slug: str
    is_favorite: bool = False
    visited: bool = False
    rating: int | None = Field(default=None, ge=1, le=5)


class PlanCreate(BaseModel):
    plan_date: date
    title: str = Field(min_length=1, max_length=180)
    mood: str = Field(default="surprise", max_length=40)
    budget: Decimal = Field(default=Decimal("100"), ge=0)
    items: list[dict] = Field(default_factory=list, max_length=12)
    notes: str = Field(default="", max_length=4000)


class PlanOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    plan_date: date
    title: str
    mood: str
    budget: Decimal
    items: list[dict]
    notes: str
    created_at: datetime
