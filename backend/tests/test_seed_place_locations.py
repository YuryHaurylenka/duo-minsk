import json
from pathlib import Path

import pytest


SEED_PLACES_PATH = Path(__file__).resolve().parents[1] / "seed" / "places.json"


@pytest.fixture(scope="module")
def places_by_slug():
    places = json.loads(SEED_PLACES_PATH.read_text(encoding="utf-8"))
    return {place["slug"]: place for place in places}


@pytest.mark.parametrize(
    ("slug", "latitude", "longitude"),
    [
        ("f1-каток-у-дворца-спорта", 53.9112083, 27.5507891),
        ("r-park", 53.9818624, 27.3178178),
        ("r-парк-лазертаг-и-троллеи", 53.9818624, 27.3178178),
        ("квест-пила", 53.9159682, 27.5218188),
        ("квест-проклятие-эмили", 53.907663, 27.531127),
        ("прогулка-по-парку-победы", 53.9225949, 27.5369616),
        ("художественная-студия-indigo", 53.927416, 27.615460),
    ],
)
def test_verified_minsk_places_keep_their_corrected_coordinates(
    places_by_slug, slug, latitude, longitude
):
    place = places_by_slug[slug]

    assert place["latitude"] == pytest.approx(latitude)
    assert place["longitude"] == pytest.approx(longitude)
    assert place["location_verified"] is True


def test_legacy_shared_fallback_coordinate_is_not_reintroduced(places_by_slug):
    for place in places_by_slug.values():
        assert (place["latitude"], place["longitude"]) != (53.8976873, 27.5494218), place["slug"]


def test_pbaza_is_not_plotted_until_its_exact_venue_point_is_confirmed(places_by_slug):
    place = places_by_slug["pbaza-пеинтбол-и-лазертаг"]

    assert place["latitude"] is None
    assert place["longitude"] is None
    assert place["location_verified"] is False
    assert "Карвата, 83А" in place["addr"]
