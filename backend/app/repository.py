"""표 ↔ 계약 모델 변환. SQL 은 여기에만 있다."""

from sqlalchemy import select

from .db import inspector_pin_replies, inspector_pins
from .schemas import PinsSaveInput, PinsSaveOutput, PinOut, Reply


class PinNotFound(Exception):
    """id 를 보냈는데 그 페이지에 그런 핀이 없는 경우."""


# 계약의 핀 필드 -> 표의 컬럼. 이름이 다른 곳은 여기 한 줄로만 이어진다.
FIELD_TO_COLUMN = {
    "s": "selector",
    "ox": "offset_x",
    "oy": "offset_y",
    "fx": "fallback_x",
    "fy": "fallback_y",
    "text": "body",
    "author": "author",
    "c": "category",
    "resolved": "resolved",
}


def _row_to_pin(row, replies: list[Reply]) -> PinOut:
    return PinOut(
        id=row.id,
        s=row.selector,
        ox=row.offset_x,
        oy=row.offset_y,
        fx=row.fallback_x,
        fy=row.fallback_y,
        text=row.body,
        author=row.author,
        c=row.category,
        resolved=row.resolved,
        replies=replies or None,
    )


def list_pins(conn, url: str, viewport: int | None = None) -> tuple[list[PinOut], int]:
    """페이지의 핀을 만든 순서대로 돌려준다.

    viewport 를 주면 그 너비로 찍힌 핀만 고른다. 핀의 ox/oy 는 대상 요소 기준
    비율이지만 fx/fy 는 픽셀이라 너비가 다르면 폴백 위치가 어긋나기 때문이다.
    """
    query = select(inspector_pins).where(inspector_pins.c.page_url == url)
    if viewport is not None:
        query = query.where(inspector_pins.c.viewport == viewport)
    rows = conn.execute(query.order_by(inspector_pins.c.id)).all()

    replies_by_pin: dict[int, list[Reply]] = {}
    if rows:
        reply_rows = conn.execute(
            select(inspector_pin_replies)
            .where(inspector_pin_replies.c.pin_id.in_([row.id for row in rows]))
            .order_by(inspector_pin_replies.c.id)
        ).all()
        for reply in reply_rows:
            replies_by_pin.setdefault(reply.pin_id, []).append(
                Reply(text=reply.body, author=reply.author)
            )

    pins = [_row_to_pin(row, replies_by_pin.get(row.id, [])) for row in rows]
    # 응답의 viewport 는 필수값이다(계약 output). 요청에 없으면 가장 최근 핀의
    # 값을 쓰고, 핀도 없으면 0 을 쓴다.
    resolved_viewport = viewport if viewport is not None else (rows[-1].viewport if rows else 0)
    return pins, resolved_viewport


def save_pin(conn, payload: PinsSaveInput) -> PinsSaveOutput:
    """핀 한 건을 만들거나 고친다. pin.id 가 없으면 새 핀이다."""
    pin = payload.pin
    sent = pin.model_fields_set  # 보내지 않은 필드는 건드리지 않는다.

    if pin.id is None:
        values = {
            "page_url": payload.url,
            # 계약상 viewport 는 선택 필드지만 컬럼은 NOT NULL 이다.
            # 플러그인은 항상 보내며, 없이 오면 0 으로 남긴다.
            "viewport": payload.viewport if payload.viewport is not None else 0,
            "selector": pin.s,
            "offset_x": pin.ox,
            "offset_y": pin.oy,
            "fallback_x": pin.fx,
            "fallback_y": pin.fy,
            "body": pin.text,
            "author": pin.author,
            "category": pin.c,
            "resolved": bool(pin.resolved),
        }
        result = conn.execute(inspector_pins.insert().values(**values))
        return PinsSaveOutput(id=result.inserted_primary_key[0], created=True)

    changes = {
        FIELD_TO_COLUMN[field]: getattr(pin, field)
        for field in sent
        if field in FIELD_TO_COLUMN
    }
    if payload.viewport is not None:
        changes["viewport"] = payload.viewport

    result = conn.execute(
        inspector_pins.update()
        .where(inspector_pins.c.id == pin.id)
        .where(inspector_pins.c.page_url == payload.url)
        .values(**changes)
    )
    if result.rowcount == 0:
        raise PinNotFound(pin.id)
    return PinsSaveOutput(id=pin.id, created=False)
