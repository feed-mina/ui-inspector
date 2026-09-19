"""SDUI 키트 표준 응답 봉투 {ok, data, errors}.

gomgom-ai 의 _ok/_error 와 같은 모양이라 플러그인 쪽 처리도 같다.
"""

from typing import Any

from fastapi.responses import JSONResponse


def ok(data: Any) -> dict:
    return {"ok": True, "data": data, "errors": []}


def error_body(code: str, message: str) -> dict:
    return {"ok": False, "data": None, "errors": [{"code": code, "message": message}]}


def error(code: str, message: str, status: int = 400) -> JSONResponse:
    return JSONResponse(error_body(code, message), status_code=status)
