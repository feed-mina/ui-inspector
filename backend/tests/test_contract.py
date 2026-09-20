"""계약 파일과 이 서버가 같은 말을 하는지 본다.

계약의 정본은 sdui/ui-inspector/contracts/*.schema.json 이고,
그 계약의 정본은 src/state.js 의 validateState 다.
여기서 깨지면 고쳐야 하는 쪽은 대개 서버지 계약이 아니다.
"""

import json

import pytest
from jsonschema import Draft202012Validator

from conftest import CONTRACT_DIR, MANIFEST_PATH
from app.db import PIN_CATEGORIES
from app.schemas import PinIn, PinsSaveInput

PAGE = "https://example.com/"
PIN = {
    "id": None,
    "s": "#main > h1",
    "ox": 0.5,
    "oy": 0.5,
    "fx": 120,
    "fy": 90,
    "text": "제목이 잘립니다",
    "c": "layout",
    "resolved": False,
}


def contract(name: str) -> dict:
    return json.loads((CONTRACT_DIR / f"{name}.schema.json").read_text(encoding="utf-8"))


def check(name: str, payload) -> None:
    Draft202012Validator(contract(name)).validate(payload)


def test_contract_files_are_valid_json_schema():
    for path in sorted(CONTRACT_DIR.glob("*.schema.json")):
        Draft202012Validator.check_schema(json.loads(path.read_text(encoding="utf-8")))


def test_list_request_and_response_match_the_contract(client):
    query = {"url": PAGE, "viewport": 1280}
    check("inspector-pins-list.input", query)

    client.post("/api/v1/inspector/pins", json={"url": PAGE, "viewport": 1280, "pin": PIN})
    body = client.get("/api/v1/inspector/pins", params=query).json()

    assert body["ok"] is True and body["errors"] == []
    check("inspector-pins-list.output", body["data"])


def test_empty_list_response_matches_the_contract(client):
    body = client.get("/api/v1/inspector/pins", params={"url": PAGE, "viewport": 1280}).json()
    check("inspector-pins-list.output", body["data"])


def test_save_request_and_response_match_the_contract(client):
    request = {"url": PAGE, "viewport": 1280, "pin": PIN}
    check("inspector-pins-save.input", request)

    body = client.post("/api/v1/inspector/pins", json=request).json()
    check("inspector-pins-save.output", body["data"])


def test_pin_required_fields_are_the_same_on_both_sides():
    contract_required = set(contract("inspector-pins-save.input")["properties"]["pin"]["required"])
    server_required = set(PinIn.model_json_schema()["required"])
    assert server_required == contract_required == {"fx", "fy", "text"}


def test_category_values_are_the_same_on_three_sides():
    from_contract = set(
        contract("inspector-pins-save.input")["properties"]["pin"]["properties"]["c"]["enum"]
    )
    from_list = set(
        contract("inspector-pins-list.output")["$defs"]["pin"]["properties"]["c"]["enum"]
    )
    # app/db.py 의 PIN_CATEGORIES 는 src/state.js 의 PIN_CATEGORIES 를 옮긴 것이고,
    # DB 의 CHECK 제약도 같은 목록이다.
    assert from_contract == from_list == set(PIN_CATEGORIES)


@pytest.mark.parametrize("field, keyword", [("text", "maxLength"), ("text", "minLength"), ("author", "maxLength")])
def test_length_limits_are_the_same_on_both_sides(field, keyword):
    from_contract = contract("inspector-pins-save.input")["properties"]["pin"]["properties"][field][keyword]
    server = PinIn.model_json_schema()["properties"][field]
    # 선택 필드는 anyOf(문자열, null) 로 풀린다.
    candidates = server.get("anyOf", [server])
    server_keyword = {"maxLength": "maxLength", "minLength": "minLength"}[keyword]
    values = [item[server_keyword] for item in candidates if server_keyword in item]
    assert values == [from_contract]


def test_url_limits_are_the_same_on_both_sides():
    save_url = contract("inspector-pins-save.input")["properties"]["url"]
    list_url = contract("inspector-pins-list.input")["properties"]["url"]
    server_url = PinsSaveInput.model_json_schema()["properties"]["url"]
    assert save_url["maxLength"] == list_url["maxLength"] == server_url["maxLength"]
    assert save_url["minLength"] == list_url["minLength"] == server_url["minLength"]


def test_schema_version_is_fixed_at_two(client):
    const = contract("inspector-pins-list.output")["properties"]["v"]["const"]
    body = client.get("/api/v1/inspector/pins", params={"url": PAGE}).json()
    # 다르면 북마클릿의 validateState 가 상태 전체를 null 로 버린다(src/state.js:51).
    assert body["data"]["v"] == const == 2


# manifest 는 계약 4장을 문자열 경로가 아니라 값으로 품고 있다. Studio 의 파일
# 가져오기가 JSON 한 장만 받기 때문이다(#manifest-file 입력에 multiple 도
# webkitdirectory 도 없다). 형제 파일을 참조하면 브라우저로는 가져올 수 없다.
MANIFEST_SCHEMAS = {
    ("actions", "inspector.pins.save", "inputSchema"): "inspector-pins-save.input",
    ("actions", "inspector.pins.save", "outputSchema"): "inspector-pins-save.output",
    ("hydrators", "inspector.pins.list", "inputSchema"): "inspector-pins-list.input",
    ("hydrators", "inspector.pins.list", "outputSchema"): "inspector-pins-list.output",
}


def manifest_plugin() -> dict:
    manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    return next(plugin for plugin in manifest["plugins"] if plugin["id"] == "ui-inspector")


def test_manifest_inlines_the_same_schemas_as_the_contract_files():
    plugin = manifest_plugin()
    for (kind, operation, key), name in MANIFEST_SCHEMAS.items():
        assert plugin["provides"][kind][operation][key] == contract(name), f"{operation}.{key}"


def test_manifest_references_no_sibling_files():
    manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    assert "contract" not in manifest.get("api", {}), "api.contract 는 파일 참조라 가져오기를 막는다"

    plugin = manifest_plugin()
    assert plugin.get("entryMode") == "host", "package entry 도 파일 참조가 된다"
    for kind in ("actions", "hydrators", "widgets"):
        for operation, definition in (plugin["provides"].get(kind) or {}).items():
            for key, value in definition.items():
                if key.endswith("Schema"):
                    assert not isinstance(value, str), f"{operation}.{key} 가 파일 경로다"


def test_manifest_declares_the_backend_origin():
    # 게시 페이지의 CSP connect-src 는 여기 선언된 출처만 허용한다
    # (키트 src/published-page.js). 빠지면 화면에서 창구 호출이 브라우저에 막힌다.
    manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    origins = manifest["api"]["origins"]
    assert origins == ["https://inspector.feedmina.tech"]

    for endpoint in manifest["api"]["endpoints"]:
        assert endpoint["path"].startswith("/api/v1/inspector/"), endpoint
