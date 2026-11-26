import json
from types import SimpleNamespace

import pytest

from app.services import event_sync


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        ("https://cdn.example.com/poster.jpg", "https://cdn.example.com/poster.jpg"),
        ("poster.webp", "https://bezkassira.by/events/minsk/poster.webp"),
        ({"url": "https://bezkassira.by/events/minsk/", "contentUrl": "https://cdn.example.com/actual-poster.webp"}, "https://cdn.example.com/actual-poster.webp"),
        ({"url": "https://cdn.example.com/poster.webp"}, "https://cdn.example.com/poster.webp"),
        ({"contentUrl": "/images/poster.jpg"}, "https://bezkassira.by/images/poster.jpg"),
        ([{"thumbnailUrl": "/images/thumb.jpg"}, {"url": "/images/full.jpg"}],
         "https://bezkassira.by/images/thumb.jpg"),
    ],
)
def test_image_url_resolves_json_ld_image_shapes(value, expected):
    assert event_sync._image_url(value, "https://bezkassira.by/events/minsk/") == expected


@pytest.mark.parametrize("value", [None, {}, [], "[object Object]", "javascript:alert(1)"])
def test_image_url_rejects_invalid_values(value):
    assert event_sync._image_url(value, "https://bezkassira.by/events/minsk/") is None


def test_parse_source_extracts_image_object_url(monkeypatch):
    event = {
        "@type": "Event",
        "name": "Test concert",
        "startDate": "2026-12-10T19:00:00+03:00",
        "url": "/events/test-concert/",
        "image": {"@type": "ImageObject", "url": "/storage/poster.webp"},
    }
    response = SimpleNamespace(
        text=f'<script type="application/ld+json">{json.dumps(event)}</script>',
        raise_for_status=lambda: None,
    )
    monkeypatch.setattr(event_sync.requests, "get", lambda *args, **kwargs: response)

    parsed = event_sync._parse_source(
        "bezkassira-concerts",
        "https://bezkassira.by/events/concert-minsk/",
    )

    assert len(parsed) == 1
    assert parsed[0]["image_url"] == "https://bezkassira.by/storage/poster.webp"
