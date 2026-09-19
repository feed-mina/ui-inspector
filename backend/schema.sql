-- ui-inspector 핀 저장용 표.
-- docs/ui-inspector-sdui-fix-guide.html 6번 단계의 스키마 그대로이며,
-- 컬럼은 src/state.js 의 validateState(스키마 버전 2) 필드를 옮긴 것이다.
--
-- 조회키(selector)와 저장 데이터(fallback_x/fallback_y/body/답글)를 분리해 둔다.
-- 앱은 SQLAlchemy 로 같은 표를 만들 수 있으므로(app/db.py) 이 파일은
-- DB 를 사람이 직접 준비할 때 쓴다.

CREATE TABLE inspector_pins (
    id          BIGSERIAL PRIMARY KEY,
    page_url    TEXT        NOT NULL,
    viewport    INTEGER     NOT NULL,
    selector    TEXT,                   -- pin.s  조회키
    offset_x    REAL CHECK (offset_x  BETWEEN 0 AND 1),   -- pin.ox
    offset_y    REAL CHECK (offset_y  BETWEEN 0 AND 1),   -- pin.oy
    fallback_x  REAL        NOT NULL,   -- pin.fx
    fallback_y  REAL        NOT NULL,   -- pin.fy
    body        TEXT        NOT NULL,   -- pin.text
    author      VARCHAR(100),
    category    VARCHAR(16) CHECK (category IN ('text','layout','missing','question')),
    resolved    BOOLEAN     NOT NULL DEFAULT false,
    created_at  TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX inspector_pins_page_idx ON inspector_pins (page_url);

CREATE TABLE inspector_pin_replies (
    id         BIGSERIAL PRIMARY KEY,
    pin_id     BIGINT NOT NULL REFERENCES inspector_pins(id) ON DELETE CASCADE,
    body       TEXT   NOT NULL,   -- reply.text
    author     VARCHAR(100),
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX inspector_pin_replies_pin_idx ON inspector_pin_replies (pin_id);
