from datetime import date, datetime
from decimal import Decimal
from uuid import UUID
from typing import Literal
from pydantic import BaseModel, ConfigDict, Field


class CityOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    slug: str
    name: str
    name_localized: str
    country_code: str
    country_name: str
    country_name_localized: str
    timezone: str
    currency_code: str
    default_language: str


class PlaceOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    slug: str
    city_slug: str
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
    latitude: float | None = None
    longitude: float | None = None
    location_verified_at: datetime | None = None
    district: str | None = None
    image_url: str | None = None
    image_source_url: str | None = None


class EventOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    city_slug: str
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
    city_slug: str
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


class CouplePreferencesIn(BaseModel):
    interests: list[Literal["Рестораны", "Кофейни", "Бары и пабы", "Активности", "Культура", "Прогулки и отдых", "Другое"]] = Field(default_factory=list, max_length=7)
    avoid: list[Literal["Бары и пабы", "Активности", "Культура", "Рестораны"]] = Field(default_factory=list, max_length=4)


class RecommendationRequest(BaseModel):
    city_slug: str = Field(default="minsk", min_length=2, max_length=80)
    interests: list[Literal["Рестораны", "Кофейни", "Бары и пабы", "Активности", "Культура", "Прогулки и отдых", "Другое"]] = Field(default_factory=list, max_length=7)
    avoid: list[Literal["Бары и пабы", "Активности", "Культура", "Рестораны"]] = Field(default_factory=list, max_length=4)
    limit: int = Field(default=6, ge=1, le=12)


class ActivitySyncItem(BaseModel):
    place_slug: str = Field(min_length=1, max_length=180)
    is_favorite: bool = False
    visited: bool = False
    rating: int | None = Field(default=None, ge=1, le=5)
    note: str = Field(default="", max_length=2000)


class PlanCreate(BaseModel):
    plan_date: date
    title: str = Field(min_length=1, max_length=180)
    mood: str = Field(default="surprise", max_length=40)
    budget: Decimal = Field(default=Decimal("100"), ge=0)
    items: list[dict] = Field(default_factory=list, max_length=12)
    notes: str = Field(default="", max_length=4000)


class PlanUpdate(BaseModel):
    expected_updated_at: datetime
    plan_date: date | None = None
    title: str | None = Field(default=None, min_length=1, max_length=180)
    mood: str | None = Field(default=None, max_length=40)
    budget: Decimal | None = Field(default=None, ge=0)
    items: list[dict] | None = Field(default=None, max_length=12)
    notes: str | None = Field(default=None, max_length=4000)


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
    updated_at: datetime


class MatchSessionCreate(BaseModel):
    city_slug: str = Field(default="minsk", min_length=2, max_length=80)
    category: str | None = Field(default=None, max_length=120)
    limit: int = Field(default=24, ge=8, le=60)


class MatchVoteIn(BaseModel):
    place_slug: str = Field(min_length=1, max_length=180)
    liked: bool
