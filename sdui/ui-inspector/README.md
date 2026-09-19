# SDUI 템플릿 패키지 — ui-inspector 댓글 패널

ui-inspector 의 화면 부품 중 **댓글 패널**을
[SDUI Template Kit](https://github.com/feed-mina/sdui-template-kit-productization) 의
Studio 편집기에서 열고 게시하기 위한 화면 정의입니다.

| 파일 | 역할 |
|---|---|
| `template.manifest.json` | 패널 화면 정의(`feedmina.sdui.template.v1`). Studio 가져오기의 입력 |
| `contracts/*.schema.json` | action·hydrator 입출력 JSON Schema 4장 |
| `api-contract.md` | 백엔드 창구 요약 |

## 무엇이 옮겨졌고 무엇이 아닌가

Studio 는 요소 24종과 스타일 11종만 받습니다(`base-elements.js`).
새 요소 종류는 `unknown element type` 으로 거부됩니다.

| ui-inspector 부품 | 처리 |
|---|---|
| `createPanel` · `createFilterToolbar` · `createCommentItem` · `filterAndSortPins` | 24종으로 재조립해 이 manifest 에 넣음 |
| `buildStyles` | `theme.tokens` 로 옮길 수 있음(색·반경·여백만) |
| `calculatePinPosition` · `repositionPin` · `createPinElement` · `restorePins` | **요소로 표현 불가.** 허용 스타일에 `position`·`left`·`top` 이 없음 → 플러그인 |
| `highlightPinTarget` · `clearPinHighlight` | 대상 페이지 DOM 조작 → 플러그인 |

## 대응하는 백엔드 창구

| manifest 선언 | 경로 |
|---|---|
| `inspector.pins.list` (hydrator) | `GET /api/v1/inspector/pins` |
| `inspector.pins.save` (action) | `POST /api/v1/inspector/pins` |

계약 스키마는 `src/state.js` 의 `validateState`(스키마 버전 2)를 그대로 옮긴 것입니다.
백엔드와 DB 는 아직 없습니다. 만드는 방법은 `docs/ui-inspector-sdui-fix-guide.html` 의
5·6번 단계에 있습니다.

## 검증

```bash
# sdui-template-kit-productization 저장소에서
node ./bin/sdui-kit.js validate <이 폴더>/template.manifest.json
node ./bin/sdui-kit.js import <이 폴더> --target cloudflare-worker-static --dry-run
```

`Manifest OK: ui-inspector-panel@0.1.0` 과 `pluginCompatibility: ready` 가 나와야 합니다.
