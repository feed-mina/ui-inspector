"""ui-inspector 핀 저장 창구.

계약: sdui/ui-inspector/contracts/*.schema.json
  GET  /api/v1/inspector/pins?url=&viewport=   hydrator inspector.pins.list
  POST /api/v1/inspector/pins                  action   inspector.pins.save

부르는 쪽은 SDUI 게시 페이지에 붙는 플러그인
(sdui-template-kit-productization 저장소 studio/sdui-ui-inspector.js)이다.

개인정보 원칙(README): 화면 내용을 밖으로 내보내지 않는다. 여기에 들어오는 것도
선택자·좌표·사람이 직접 쓴 글뿐이며, 대상 페이지의 텍스트나 HTML 은 받지 않는다.
"""

from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI, Query
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from starlette.exceptions import HTTPException as StarletteHTTPException

from . import config, repository
from .db import engine, metadata
from .envelope import error, ok
from .schemas import PinsListOutput, PinsSaveInput


@asynccontextmanager
async def lifespan(app: FastAPI):
    if config.CREATE_TABLES:
        metadata.create_all(engine)
    yield
    engine.dispose()


app = FastAPI(
    title="ui-inspector pins API",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=config.ALLOWED_ORIGINS,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["Content-Type"],
    max_age=600,
)


def get_connection():
    """요청 하나가 트랜잭션 하나다."""
    with engine.begin() as connection:
        yield connection


@app.exception_handler(RequestValidationError)
async def on_validation_error(request, exc: RequestValidationError):
    first = exc.errors()[0]
    where = ".".join(str(part) for part in first["loc"][1:]) or first["loc"][0]
    return error("VALIDATION_ERROR", f"{where}: {first['msg']}")


@app.exception_handler(StarletteHTTPException)
async def on_http_error(request, exc: StarletteHTTPException):
    codes = {404: "NOT_FOUND", 405: "METHOD_NOT_ALLOWED"}
    return error(codes.get(exc.status_code, "PLUGIN_ERROR"), str(exc.detail), status=exc.status_code)


@app.get("/healthz")
def healthz():
    return ok({"status": "ok"})


@app.get("/api/v1/inspector/pins")
def list_pins(
    url: str = Query(min_length=1, max_length=2048, description="주석 대상 페이지 주소. state.url 과 같은 값"),
    viewport: int | None = Query(default=None, ge=1, description="기준 뷰포트 너비"),
    connection=Depends(get_connection),
):
    pins, resolved_viewport = repository.list_pins(connection, url, viewport)
    # v 가 2 가 아니면 북마클릿의 validateState 가 상태 전체를 버린다(src/state.js:51).
    return ok(PinsListOutput(url=url, viewport=resolved_viewport, pins=pins).model_dump(exclude_none=True))


@app.post("/api/v1/inspector/pins")
def save_pin(payload: PinsSaveInput, connection=Depends(get_connection)):
    try:
        saved = repository.save_pin(connection, payload)
    except repository.PinNotFound:
        return error("NOT_FOUND", f"이 페이지에 id {payload.pin.id} 인 핀이 없습니다.", status=404)
    return ok(saved.model_dump())
