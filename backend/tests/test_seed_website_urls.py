import json
from pathlib import Path
from urllib.parse import urlparse


SEED_PLACES_PATH = Path(__file__).resolve().parents[1] / "seed" / "places.json"


def is_generic_search_or_map_url(value):
    if not value:
        return False
    parsed = urlparse(value)
    host = (parsed.hostname or "").lower().removeprefix("www.")
    path = parsed.path.lower()
    google = host == "google.com" and (
        path == "/search" or path.startswith("/search/")
        or path == "/maps" or path.startswith("/maps/")
    )
    yandex = (
        host in {"yandex.by", "yandex.com", "yandex.ru"}
        or host.endswith(".yandex.by")
        or host.endswith(".yandex.ru")
    ) and path.startswith("/maps")
    return google or yandex


def test_seed_website_field_contains_only_official_venue_sites():
    places = json.loads(SEED_PLACES_PATH.read_text(encoding="utf-8"))

    invalid = [
        (place.get("n"), place.get("site"))
        for place in places
        if is_generic_search_or_map_url(place.get("site"))
    ]

    assert invalid == []
