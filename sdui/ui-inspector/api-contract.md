# ui-inspector API Contract

상태 모델은 `src/state.js` 의 `validateState`(스키마 버전 2)를 그대로 따른다.
응답 봉투는 SDUI 키트 표준인 `{ "ok": ..., "data": ..., "errors": [] }`.

## GET /api/v1/inspector/pins?url=&viewport=

대상 페이지의 핀 목록을 돌려준다. hydrator `inspector.pins.list` 가 호출한다.

## POST /api/v1/inspector/pins

핀 한 건을 저장한다. `pin.id` 가 없으면 새로 만든다.
action `inspector.pins.save` 가 호출한다.

조회키와 저장키의 구분은 어제 인수인계 문서와 같다.
`pin.s` 는 화면 요소를 다시 찾기 위한 조회키이고,
`pin.fx`/`pin.fy`/`pin.text`/`pin.replies` 는 보관용 저장 데이터다.

## 구현

이 계약의 서버 구현은 저장소의 [`backend/`](../../backend/) 에 있습니다(FastAPI).
`backend/tests/test_contract.py` 가 실제 요청·응답을 이 폴더의 스키마로 검사합니다.
