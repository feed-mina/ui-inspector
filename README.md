# ui-inspector

살아 있는 웹페이지에서 요소를 클릭해 댓글을 다는 북마클릿.
사내 웹 프로젝트 전체에 **프로젝트 코드를 고치지 않고** 붙이는 것이 목표입니다.

설계 문서: [`feed-mina/work-cycle` → `docs/ui-inspector-design.md`](https://github.com/feed-mina/work-cycle/blob/main/docs/ui-inspector-design.md)

---

## ⚠️ 현재 상태: 작업 전 단계입니다

**이 저장소에는 아직 동작하는 인스펙터가 없습니다.**
지금 들어 있는 것은 [Pinment](https://github.com/khawkins98/pinment)에서 가져온
**참고용 코드**이며, 정리 중입니다.

```
src/bookmarklet/ui.js    핀·댓글 UI. 여기서 쓸 함수를 골라낸다
src/state.js             URL 공유 전용. 핀 스키마 검증만 옮기고 삭제 예정
tests/                   위 두 파일의 원본 테스트
```

새 진입점(`index.js`)·선택자(`selector.js`)·`version.js`·빌드 설정은 **아직 올라오지 않았습니다.**

그래서 **테스트가 절반만 돕니다.**

```
tests/state.test.js        60개 통과
tests/bookmarklet.test.js  실행 불가 — ui.js 가 없는 ../selector.js 를 import 한다
```

이 상태는 정리 작업 이전부터 그랬습니다(`main`에서도 동일). 나머지 파일이 올라와야
`bookmarklet.test.js`가 비로소 돌아갑니다.

## 지금까지 제거한 것

공개 저장소이므로, 쓰지 않기로 한 기능부터 먼저 들어냈습니다.

| 제거 | 이유 |
|---|---|
| `src/bookmarklet/pdf-export.js` | 실행 중 cdnjs에서 html2canvas·jsPDF를 내려받고, `html2canvas(document.body)`로 **화면 전체를 이미지로** 만들어 PDF로 저장. 회사 화면을 다루는 도구에 둘 수 없음 |
| `scripts/build-bookmarklet.js` | 외부 서버에서 스크립트를 받아오는 **로더**를 생성. 서버가 바뀌면 이미 설치된 북마클릿 동작도 바뀜 |
| `package.json`의 `build:bookmarklet` | 위 스크립트를 부르는 입구 |

이로써 코드에서 외부로 나가는 통신과 화면 캡처가 **모두 사라졌습니다**
(`cdnjs` · `html2canvas` · `jspdf` · `toDataURL` · `YOUR_BASE_URL` 검색 결과 0건).

> 파일을 지워도 **git 기록에는 남습니다.** "저장소가 그 기능을 보유하지 않는다"가
> 아니라 **"현재 코드에는 없다"** 가 정확한 표현입니다.

## 남은 정리

- [ ] M1 코드(`index.js` · `selector.js` · 빌드 설정) push
- [ ] `ui.js`에서 쓸 함수만 골라내기
      — 살릴 것: `calculatePinPosition` `repositionPin` `createPinElement` `createPanel`
        `restorePins` `filterAndSortPins` `buildStyles` `highlightPinTarget` `clearPinHighlight`
      — 버릴 것: `createShareModal` `createDocsSiteModal` `createWelcomeModal` `createMobileWarningModal`
- [ ] `state.js` 삭제 (핀 스키마 검증 `validateState`만 새 파일로 이관)
- [ ] `lz-string` 제거 — `state.js`가 유일한 사용처
- [ ] 새 코드를 직접 검증하는 테스트 추가
- [ ] `INCLUDED_FILES.txt` 삭제 (정리가 끝나면 역할이 끝남)

## 원칙

- **회사 화면의 내용을 외부로 내보내지 않는다** — 스크린샷·PDF·외부 CDN·`outerHTML` 모두 제외
- **북마클릿에 토큰을 심지 않는다** — 북마크 주소는 평문이다
- 검증은 `package.json`이 아니라 **코드와 빌드 결과물**에서 한다

## 라이선스

MIT. Pinment(© 2026 Ken Hawkins)에서 파생했으며 원 저작권 고지를 [`LICENSE`](LICENSE)에 보존합니다.
