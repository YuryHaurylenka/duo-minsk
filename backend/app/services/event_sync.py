"""Structured-data event importer. Sources are intentionally allow-listed."""
from datetime import datetime, timezone
import json
import re
from uuid import uuid4
from urllib.parse import urljoin, urlparse
import requests
from bs4 import BeautifulSoup
from sqlalchemy.dialects.postgresql import insert
from app.models.entities import DuoEvent

SOURCES = {
    "hubl-minsk": ("Hubl Minsk", "https://hubl.by/minsk/afisha", "minsk"),
    "bezkassira-concerts": ("BezKassira — концерты", "https://bezkassira.by/events/concert-minsk/", "minsk"),
    "bezkassira-culture": ("BezKassira — культура", "https://bezkassira.by/events/culture-minsk/", "minsk"),
}


def _walk_events(node):
    if isinstance(node, dict):
        typ = node.get("@type")
        if typ == "Event" or isinstance(typ, list) and "Event" in typ:
            yield node
        for value in node.values():
            yield from _walk_events(value)
    elif isinstance(node, list):
        for value in node:
            yield from _walk_events(value)


def _image_url(value, base_url):
    """Resolve JSON-LD image values to a safe absolute HTTP(S) URL."""
    if isinstance(value, list):
        for item in value:
            resolved = _image_url(item, base_url)
            if resolved:
                return resolved
        return None
    if isinstance(value, dict):
        for key in ("contentUrl", "thumbnailUrl", "url", "@id"):
            resolved = _image_url(value.get(key), base_url)
            if resolved:
                return resolved
        return None
    if not isinstance(value, str):
        return None
    candidate = value.strip()
    if not candidate or candidate.lower() == "[object object]":
        return None
    resolved = urljoin(base_url, candidate)
    parsed = urlparse(resolved)
    return resolved if parsed.scheme in {"http", "https"} and parsed.netloc else None


def _text(value):
    if isinstance(value, dict):
        return value.get("name") or value.get("@id") or ""
    return str(value or "")


def _parse_source(key, url, city_slug="minsk"):
    response = requests.get(url, timeout=20, headers={"User-Agent": "DUO event indexer/1.0"})
    response.raise_for_status()
    soup = BeautifulSoup(response.text, "html.parser")
    items = []
    for script in soup.select('script[type="application/ld+json"]'):
        try:
            payload = json.loads(script.string or script.get_text())
        except (ValueError, TypeError):
            continue
        for event in _walk_events(payload):
            title, start = _text(event.get("name")), event.get("startDate")
            if not title or not start:
                continue
            location = event.get("location") or {}
            address = location.get("address") or {}
            if isinstance(address, dict):
                address = ", ".join(filter(None, [address.get("streetAddress"), address.get("addressLocality")]))
            offers = event.get("offers") or {}
            if isinstance(offers, list):
                offers = offers[0] if offers else {}
            price = offers.get("price") if isinstance(offers, dict) else None
            try:
                price = float(re.sub(r"[^0-9.]", "", str(price))) if price not in (None, "") else None
            except ValueError:
                price = None
            event_url = urljoin(
                url,
                event.get("url")
                or (offers.get("url") if isinstance(offers, dict) else "")
                or "#"+re.sub(r"[^a-z0-9]+", "-", title.lower())+"-"+str(start),
            )
            items.append({
                "city_slug": city_slug,
                "source_key": key, "source_url": event_url, "title": title[:500],
                "description": BeautifulSoup(str(event.get("description") or ""), "html.parser").get_text(" ", strip=True)[:4000],
                "category": _text(event.get("eventType")) or "Событие", "venue": _text(location.get("name")),
                "address": str(address)[:500], "starts_at": start, "ends_at": event.get("endDate"),
                "price_min": price, "price_max": price, "currency": "BYN",
                "image_url": _image_url(event.get("image"), event_url),
                "ticket_url": offers.get("url") if isinstance(offers, dict) else None,
                "status": "scheduled", "last_verified_at": datetime.now(timezone.utc),
            })
    return items


def sync_events(db):
    total, failures = 0, []
    for key, (_, url, city_slug) in SOURCES.items():
        try:
            items = _parse_source(key, url, city_slug)
            for item in items:
                stmt = insert(DuoEvent).values(id=uuid4(), **item, created_at=datetime.now(timezone.utc), updated_at=datetime.now(timezone.utc)).on_conflict_do_update(
                    constraint="duo_events_source_key_source_url_key",
                    set_={**item, "updated_at": datetime.now(timezone.utc)},
                )
                db.execute(stmt)
            total += len(items)
        except Exception as exc:
            failures.append({"source": key, "error": str(exc)[:300]})
    db.commit()
    return {"upserted": total, "failures": failures, "checked_at": datetime.now(timezone.utc).isoformat()}
