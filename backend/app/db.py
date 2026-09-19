"""표 정의와 엔진. schema.sql 과 같은 표를 SQLAlchemy 로 적은 것이다.

Postgres 를 기준으로 쓰되, 로컬에서 DB 없이 띄워 볼 수 있도록 SQLite 에서도
같은 표가 만들어지게 타입을 variant 로 적었다.
"""

from sqlalchemy import (
    BigInteger,
    Boolean,
    CheckConstraint,
    Column,
    DateTime,
    REAL,
    ForeignKey,
    Index,
    Integer,
    MetaData,
    String,
    Table,
    Text,
    create_engine,
    func,
)
from sqlalchemy.sql import expression

from . import config

# src/state.js 의 PIN_CATEGORIES 와 같아야 한다.
PIN_CATEGORIES = ("text", "layout", "missing", "question")

metadata = MetaData()

# SQLite 는 BIGSERIAL 자동 증가를 INTEGER PRIMARY KEY 로만 지원한다.
_PK = BigInteger().with_variant(Integer, "sqlite")

inspector_pins = Table(
    "inspector_pins",
    metadata,
    Column("id", _PK, primary_key=True, autoincrement=True),
    Column("page_url", Text, nullable=False),
    Column("viewport", Integer, nullable=False),
    Column("selector", Text),                       # pin.s  조회키
    Column("offset_x", REAL),                      # pin.ox
    Column("offset_y", REAL),                      # pin.oy
    Column("fallback_x", REAL, nullable=False),    # pin.fx
    Column("fallback_y", REAL, nullable=False),    # pin.fy
    Column("body", Text, nullable=False),           # pin.text
    Column("author", String(100)),
    Column("category", String(16)),
    Column("resolved", Boolean, nullable=False, server_default=expression.false()),
    Column("created_at", DateTime(timezone=True), nullable=False, server_default=func.now()),
    CheckConstraint("offset_x BETWEEN 0 AND 1", name="inspector_pins_offset_x_check"),
    CheckConstraint("offset_y BETWEEN 0 AND 1", name="inspector_pins_offset_y_check"),
    CheckConstraint(
        "category IN ('text','layout','missing','question')",
        name="inspector_pins_category_check",
    ),
    Index("inspector_pins_page_idx", "page_url"),
)

inspector_pin_replies = Table(
    "inspector_pin_replies",
    metadata,
    Column("id", _PK, primary_key=True, autoincrement=True),
    Column(
        "pin_id",
        BigInteger().with_variant(Integer, "sqlite"),
        ForeignKey("inspector_pins.id", ondelete="CASCADE"),
        nullable=False,
    ),
    Column("body", Text, nullable=False),           # reply.text
    Column("author", String(100)),
    Column("created_at", DateTime(timezone=True), nullable=False, server_default=func.now()),
    Index("inspector_pin_replies_pin_idx", "pin_id"),
)


def create_engine_from_config(url: str | None = None):
    return create_engine(url or config.DATABASE_URL, future=True)


engine = create_engine_from_config()
