"""창구 동작. 부르는 쪽은 키트의 studio/sdui-ui-inspector.js 다."""

PAGE = "https://example.com/"
NEW_PIN = {
    "id": None,          # 플러그인은 새 핀에 항상 null 을 보낸다
    "s": "#main > h1",
    "ox": 0.5,
    "oy": 0.5,
    "fx": 120,
    "fy": 90,
    "text": "제목이 잘립니다",
    "c": "layout",
    "resolved": False,
}


def save(client, pin, url=PAGE, viewport=1280):
    return client.post("/api/v1/inspector/pins", json={"url": url, "viewport": viewport, "pin": pin})


def test_empty_list_still_has_schema_version(client):
    response = client.get("/api/v1/inspector/pins", params={"url": PAGE, "viewport": 1280})
    assert response.status_code == 200
    body = response.json()
    assert body["ok"] is True and body["errors"] == []
    # v 가 2 가 아니면 북마클릿의 validateState 가 상태 전체를 버린다.
    assert body["data"] == {"v": 2, "url": PAGE, "viewport": 1280, "pins": []}


def test_saved_pin_comes_back_in_the_list(client):
    saved = save(client, NEW_PIN).json()
    assert saved["ok"] is True
    assert saved["data"]["created"] is True
    pin_id = saved["data"]["id"]

    pins = client.get("/api/v1/inspector/pins", params={"url": PAGE, "viewport": 1280}).json()["data"]["pins"]
    assert len(pins) == 1
    assert pins[0]["id"] == pin_id
    assert pins[0]["s"] == "#main > h1"
    assert pins[0]["fx"] == 120 and pins[0]["fy"] == 90
    assert pins[0]["text"] == "제목이 잘립니다"
    assert pins[0]["c"] == "layout"
    assert pins[0]["resolved"] is False


def test_second_save_with_id_updates_instead_of_adding(client):
    pin_id = save(client, NEW_PIN).json()["data"]["id"]

    again = save(client, {**NEW_PIN, "id": pin_id, "text": "고쳤습니다", "resolved": True}).json()
    assert again["data"] == {"id": pin_id, "created": False}

    pins = client.get("/api/v1/inspector/pins", params={"url": PAGE, "viewport": 1280}).json()["data"]["pins"]
    assert len(pins) == 1
    assert pins[0]["text"] == "고쳤습니다"
    assert pins[0]["resolved"] is True


def test_unknown_id_is_not_silently_created(client):
    response = save(client, {**NEW_PIN, "id": 9999})
    assert response.status_code == 404
    body = response.json()
    assert body["ok"] is False
    assert body["errors"][0]["code"] == "NOT_FOUND"
    assert body["data"] is None


def test_pin_of_another_page_is_not_reachable(client):
    pin_id = save(client, NEW_PIN).json()["data"]["id"]

    other = client.get("/api/v1/inspector/pins", params={"url": "https://example.com/other", "viewport": 1280})
    assert other.json()["data"]["pins"] == []

    # 같은 id 라도 페이지가 다르면 고칠 수 없다.
    assert save(client, {**NEW_PIN, "id": pin_id}, url="https://example.com/other").status_code == 404


def test_viewport_filters_the_list(client):
    save(client, NEW_PIN, viewport=1280)
    save(client, NEW_PIN, viewport=375)

    wide = client.get("/api/v1/inspector/pins", params={"url": PAGE, "viewport": 1280}).json()["data"]
    assert len(wide["pins"]) == 1 and wide["viewport"] == 1280

    # viewport 를 빼면 너비로 거르지 않는다.
    everything = client.get("/api/v1/inspector/pins", params={"url": PAGE}).json()["data"]
    assert len(everything["pins"]) == 2
    assert everything["viewport"] == 375  # 가장 최근 핀의 값


def test_replies_ride_along_with_the_pin(client, engine):
    from app.db import inspector_pin_replies

    pin_id = save(client, NEW_PIN).json()["data"]["id"]

    # 답글 창구는 아직 없다. 표에 직접 넣어 목록에 실리는지만 본다.
    with engine.begin() as connection:
        connection.execute(
            inspector_pin_replies.insert().values(pin_id=pin_id, body="저도 보입니다", author="minsu")
        )

    pins = client.get("/api/v1/inspector/pins", params={"url": PAGE, "viewport": 1280}).json()["data"]["pins"]
    assert pins[0]["replies"] == [{"text": "저도 보입니다", "author": "minsu"}]


def test_bad_category_is_rejected(client):
    response = save(client, {**NEW_PIN, "c": "감상"})
    assert response.status_code == 400
    assert response.json()["errors"][0]["code"] == "VALIDATION_ERROR"


def test_empty_comment_is_rejected(client):
    response = save(client, {**NEW_PIN, "text": "   "})
    assert response.status_code == 400
    assert response.json()["errors"][0]["code"] == "VALIDATION_ERROR"


def test_offset_out_of_range_is_rejected(client):
    assert save(client, {**NEW_PIN, "ox": 1.5}).status_code == 400


def test_absurdly_long_url_is_rejected(client):
    long_url = "https://example.com/" + "a" * 3000
    assert save(client, NEW_PIN, url=long_url).status_code == 400
    assert client.get("/api/v1/inspector/pins", params={"url": long_url}).status_code == 400


def test_url_is_required_on_the_list(client):
    response = client.get("/api/v1/inspector/pins")
    assert response.status_code == 400
    assert response.json()["errors"][0]["code"] == "VALIDATION_ERROR"


def test_cors_allows_only_the_published_page(client):
    allowed = client.get(
        "/api/v1/inspector/pins",
        params={"url": PAGE},
        headers={"Origin": "https://sdui-template-kit-productization.pages.dev"},
    )
    assert allowed.headers["access-control-allow-origin"] == "https://sdui-template-kit-productization.pages.dev"

    stranger = client.get(
        "/api/v1/inspector/pins",
        params={"url": PAGE},
        headers={"Origin": "https://attacker.example"},
    )
    assert "access-control-allow-origin" not in stranger.headers


def test_healthz(client):
    assert client.get("/healthz").json() == {"ok": True, "data": {"status": "ok"}, "errors": []}
