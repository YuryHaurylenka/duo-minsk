import json
import re
import unicodedata
from datetime import datetime, timezone
from pathlib import Path
from sqlalchemy import select
from app.database import SessionLocal
from app.models.entities import Place


def slugify(value: str) -> str:
    value = unicodedata.normalize("NFD", value.lower().strip())
    value = "".join(char for char in value if not unicodedata.combining(char))
    value = re.sub(r"[^a-zа-яё0-9]+", "-", value, flags=re.I).strip("-")
    return value[:170] or "place"


def main():
    source = Path(__file__).parent / "seed" / "places.json"
    records = json.loads(source.read_text(encoding="utf-8"))
    with SessionLocal() as db:
        for item in records:
            slug = item.get("slug") or slugify(item["n"])
            row = db.scalar(select(Place).where(Place.slug == slug))
            values = dict(name=item["n"], category=item.get("cat", "Другое"), emoji=item.get("emoji", "✨"), description=item.get("desc", ""), address=item.get("addr", ""), rating=str(item.get("rating", "—")), reviews=str(item.get("reviews", "—")), price_label=item.get("price", ""), couple_price_label=item.get("couple", ""), level=int(item.get("level", 1)), risk=item.get("risk", "good"), tip=item.get("why", ""), website_url=item.get("site", ""), source_name=item.get("source", ""), source_url=item.get("src", ""), cost=item.get("cost") if item.get("cost") != 999 else None, latitude=item.get("latitude"), longitude=item.get("longitude"), location_verified_at=datetime.now(timezone.utc) if item.get("location_verified") else None, district=item.get("district"), image_url=item.get("image_url"), image_source_url=item.get("image_source_url"), is_active=True)
            if row:
                for key, value in values.items():
                    setattr(row, key, value)
            else:
                db.add(Place(slug=slug, **values))
        db.commit()
    print(f"Imported {len(records)} places")


if __name__ == "__main__":
    main()
