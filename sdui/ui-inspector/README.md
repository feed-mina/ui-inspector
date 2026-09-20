# SDUI 템플릿 패키지 — ui-inspector 댓글 패널

ui-inspector 의 화면 부품 중 **댓글 패널**을
[SDUI Template Kit](https://github.com/feed-mina/sdui-template-kit-productization) 의
Studio 편집기에서 열고 게시하기 위한 화면 정의입니다.

| 파일 | 역할 |
|---|---|
| `template.manifest.json` | 패널 화면 정의(`feedmina.sdui.template.v1`). Studio 가져오기의 입력 |
| `contracts/*.schema.json` | action·hydrator 입출력 JSON Schema 4장. 계약의 정본 |
| `api-contract.md` | 백엔드 창구 요약 |

**manifest 는 계약 4장을 파일 경로가 아니라 값으로 품고 있습니다.** Studio 의
파일 가져오기는 JSON 한 장만 받아서(입력에 `multiple` 도 `webkitdirectory` 도 없음)
형제 파일을 함께 줄 방법이 없기 때문입니다. 경로로 두면
`패키지 파일을 찾을 수 없습니다` 로 가져오기가 막힙니다.

두 쪽이 갈라지지 않도록 `backend/tests/test_contract.py` 가 manifest 안의 스키마와
`contracts/` 의 파일이 같은지 확인합니다. 계약을 고칠 때는 `contracts/` 를 고치고
manifest 에도 같은 내용을 넣어야 합니다.

## 무엇이 옮겨졌고 무엇이 아닌가

Studio 는 요소 24종과 스타일 11종만 받습니다(`base-elements.js`).
새 요소 종류는 `unknown element type` 으로 거부됩니다.

| ui-inspector 부품 | 처리 |
|---|---|
| `createPanel` · `createFilterToolbar` · `createCommentItem` · `filterAndSortPins` | 24종으로 재조립해 이 manifest 에 넣음 |
| `buildStyles` | `theme.tokens` 로 옮길 수 있음(색·반경·여백만) |
| `calculatePinPosition` · `repositionPin` · `createPinElement` · `restorePins` | **요소로 표현 불가.** 허용 스타일에 `position`·`left`·`top` 이 없음 → 플러그인 |
| `highlightPinTarget` · `clearPinHighlight` | 대상 페이지 DOM 조작 → 플러그인 |

## 부르는 주소를 선언합니다

```json
"api": { "origins": ["https://inspector.feedmina.tech"], "endpoints": [ … ] }
```

게시 페이지의 보안 정책(CSP)은 기본이 `connect-src 'self'` 라, 선언하지 않으면
브라우저가 창구 호출을 막습니다. `api.origins` 에 적힌 https 출처만 허용 목록에
들어갑니다. 창구를 다른 주소로 옮기면 이 값과 키트의 플러그인 기본 주소를 함께
바꿔야 합니다 — 둘 중 하나만 바뀌면 끊깁니다.

## 대응하는 백엔드 창구

| manifest 선언 | 경로 |
|---|---|
| `inspector.pins.list` (hydrator) | `GET /api/v1/inspector/pins` |
| `inspector.pins.save` (action) | `POST /api/v1/inspector/pins` |

계약 스키마는 `src/state.js` 의 `validateState`(스키마 버전 2)를 그대로 옮긴 것입니다.
이 두 창구의 구현은 [`backend/`](../../backend/) 에 FastAPI 로 있습니다
(표 두 개는 `backend/schema.sql`). 설계 근거는 `docs/ui-inspector-sdui-fix-guide.html` 의
5·6번 단계입니다.

## 검증

```bash
# sdui-template-kit-productization 저장소에서
node ./bin/sdui-kit.js validate <이 폴더>/template.manifest.json
node ./bin/sdui-kit.js import <이 폴더> --target cloudflare-worker-static --dry-run
```

`Manifest OK: ui-inspector-panel@0.1.0` 과 `pluginCompatibility: ready` 가 나와야 합니다.
