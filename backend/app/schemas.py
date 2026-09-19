"""요청·응답 모델. sdui/ui-inspector/contracts/*.schema.json 을 그대로 옮긴 것이다.

원본 명세는 src/state.js 의 validateState(스키마 버전 2)이고,
계약 4장은 거기서 나왔다. 이 파일은 그 계약의 파이썬 표현이며
tests/test_contract.py 가 두 쪽이 같은지 확인한다.
"""

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

# src/state.js 의 SCHEMA_VERSION
SCHEMA_VERSION = 2

Category = Literal["text", "layout", "missing", "question"]


class Reply(BaseModel):
    """pin.replies[] 한 건."""

    model_config = ConfigDict(extra="ignore")

    text: str
    author: str | None = None


class PinOut(BaseModel):
    """목록 응답에 실리는 핀. contracts/inspector-pins-list.output.schema.json 의 $defs.pin."""

    model_config = ConfigDict(extra="ignore")

    id: int
    s: str | None = None
    ox: float | None = None
    oy: float | None = None
    fx: float
    fy: float
    text: str
    author: str | None = None
    c: Category | None = None
    resolved: bool | None = None
    replies: list[Reply] | None = None


class PinsListOutput(BaseModel):
    """contracts/inspector-pins-list.output.schema.json.

    v 가 2 가 아니면 북마클릿의 validateState 가 상태 전체를 버린다(src/state.js:51).
    """

    model_config = ConfigDict(extra="ignore")

    v: Literal[2] = SCHEMA_VERSION
    url: str
    viewport: int
    pins: list[PinOut]


class PinIn(BaseModel):
    """저장 요청의 pin. contracts/inspector-pins-save.input.schema.json 의 pin."""

    # 앞뒤 공백은 버린 뒤 길이를 본다. 플러그인도 보내기 전에 같은 일을 한다.
    model_config = ConfigDict(extra="ignore", str_strip_whitespace=True)

    # 없거나 null 이면 새 핀. 플러그인은 새 핀에 항상 null 을 보낸다
    # (키트 studio/sdui-ui-inspector.js 의 pendingPin).
    id: int | None = None
    s: str | None = None
    ox: float | None = Field(default=None, ge=0, le=1)
    oy: float | None = Field(default=None, ge=0, le=1)
    fx: float
    fy: float
    text: str = Field(min_length=1, max_length=2000)
    author: str | None = Field(default=None, max_length=100)
    c: Category | None = None
    resolved: bool | None = None


class PinsSaveInput(BaseModel):
    """contracts/inspector-pins-save.input.schema.json."""

    model_config = ConfigDict(extra="ignore", str_strip_whitespace=True)

    # 플러그인이 보내는 값은 location.origin + location.pathname 이라 짧다.
    url: str = Field(min_length=1, max_length=2048)
    viewport: int | None = Field(default=None, ge=1)
    pin: PinIn


class PinsSaveOutput(BaseModel):
    """contracts/inspector-pins-save.output.schema.json."""

    model_config = ConfigDict(extra="ignore")

    id: int
    created: bool
