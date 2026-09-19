# ui-inspector — easy-guide 쉬운 업데이트 설명

한국시간 2026년 9월 18~19일 업데이트 보고서. 활동 집계 마감은 9월 19일 21:24:15입니다.

화면의 위치에 핀을 찍고 의견을 남기는 도구입니다. 이번에는 화면편집기용 구성과 실제 핀 저장 서버가 추가됐습니다.

| 항목 | 기준 |
|---|---|
| 보고서 범위 | 이번 기간의 변경과 관련 기능. 전체 시스템 설명은 아래 기존 상세 문서로 연결합니다. |
| 확인 브랜치 | main |
| 소스 기준 | `80d9cff0ae15` |
| 검증 범위 | API·저장소·스키마·테스트 파일과 배포 안내를 정적으로 대조했습니다. 기존 자동화 기록만으로 운영 배포를 완료로 처리하지 않았습니다. |
| 보고서 세트 | [쉬운 설명](easy-guide.md) · [수정·검증 지시](fix-guide.md) · [코드 인수인계](screen-code-handover.md) |

## 이번에 달라진 것

- 9월 18일 인수인계 PDF를 추가했습니다.
- 9월 19일 댓글 패널 manifest·easy/fix 가이드를 추가하고 FastAPI 핀 조회·저장 서버를 구현했습니다.
- 배포 안내 커밋은 21:15에 작성됐고 PR #5의 병합은 집계 마감 직후 21:24:33입니다. 커밋 활동과 병합 시각을 구분합니다.

## 1. 용어와 원리

| 용어 | 쉬운 뜻과 이번 작업에서의 역할 |
|---|---|
| FastAPI | Python으로 요청·응답 서버를 만드는 도구입니다. |
| 트랜잭션 (Transaction) | 여러 DB 작업을 한 요청 단위로 묶어 처리하는 방식입니다. |
| Viewport (뷰포트) | 브라우저 화면의 너비입니다. 핀의 픽셀 위치가 달라질 수 있어 조회 조건으로 사용합니다. |

## 2. 익숙한 상황에 빗대어 보기

화면 위에 붙인 메모를 공용 메모함에 보관할 수 있게 만든 작업입니다. 메모가 어느 페이지·어느 화면 너비에서 붙었는지 함께 저장해야 다시 같은 위치를 찾을 수 있습니다.

이 비유는 역할을 이해하기 위한 설명입니다. 실제 저장·승인·실행 조건은 코드 인수인계 보고서를 기준으로 확인합니다.

## 3. 서로 어떻게 연결되는가

Studio 플러그인이 페이지 주소와 너비로 핀을 조회합니다. 저장 서버는 요청을 검사하고 DB 열 이름으로 바꿔 저장한 뒤 식별값을 반환합니다. 서버 코드가 있다는 사실과 실제 도메인에 배포됐다는 사실은 구분합니다.

| 산출물 | 읽고 판단할 일 |
|---|---|
| easy-guide | 무엇이 달라졌고 어디까지 가능한지 이해 |
| fix-guide | 구현된 핀 API의 실제 배포·왕복 저장 확인 |
| screen-code-handover | 화면·함수·입력·출력·저장 위치를 따라 유지보수 |

## 4. 직접 확인하는 순서

1. backend README에서 GET과 POST 예제를 읽습니다. 성공 기준: 조회와 저장의 입력이 다름을 이해합니다.
2. 로컬 DB에서 가상 페이지 핀을 저장하고 같은 주소·너비로 다시 조회합니다. 성공 기준: 반환한 ID와 내용이 일치합니다.
3. 배포는 DEPLOY 안내의 인증 경계와 도메인을 확인한 뒤 별도로 수행합니다. 이번 보고서는 실제 배포 성공을 판정하지 않습니다.

## 확인한 활동

| 한국시간 | 커밋 | 기록된 작업 | 구분 |
|---|---|---|---|
| 09/19 21:15 | [80d9cff](https://github.com/feed-mina/ui-inspector/commit/80d9cff0ae15c40f1c5e5606b6beed66da6267ad) | docs(backend): 호스팅어 VPS 배포 순서를 적는다 | 변경 기록 |
| 09/19 20:44 | [6cee30d](https://github.com/feed-mina/ui-inspector/commit/6cee30d9f80ec80dc5e96840c69b54085d3aed86) | Merge pull request #4 from feed-mina/backend/fastapi-pins | 병합 기록 |
| 09/19 20:37 | [4ab2334](https://github.com/feed-mina/ui-inspector/commit/4ab23347594eb01cd1d590a2626c51ca228749a1) | feat(backend): 핀 저장 창구를 FastAPI 로 구현 | 변경 기록 |
| 09/19 16:34 | [dfe0ad2](https://github.com/feed-mina/ui-inspector/commit/dfe0ad243b0cbbb7db4e108b0d2ce6a3c12f22ab) | Merge pull request #3 from feed-mina/sdui/inspector-panel | 병합 기록 |
| 09/19 16:08 | [055993a](https://github.com/feed-mina/ui-inspector/commit/055993a1bdaf6bee00b433251591977cae1f0ee0) | docs(sdui): 댓글 패널 SDUI 패키지와 옮기기 가이드 2종 추가 | 변경 기록 |
| 09/18 19:14 | [ab89f8d](https://github.com/feed-mina/ui-inspector/commit/ab89f8d1b38af2d9f987cf9c0a5a226db74ba9d8) | Merge pull request #2 from feed-mina/copilot/create-handoff-documentation | 병합 기록 |
| 09/18 19:13 | [56f9a9d](https://github.com/feed-mina/ui-inspector/commit/56f9a9d81c906a23904bebabd783d5d276fb3bf4) | docs: add ui-inspector handover PDF | 변경 기록 |

커밋은 파일 변경 기록이고 병합은 작업 브랜치를 합친 기록입니다. 둘을 별개의 기능 수로 세지 않습니다. 에이전트가 작성한 커밋도 사용자 저장소의 작업으로 포함했습니다.

## 기존 상세 자료

- [백엔드 사용법](https://github.com/feed-mina/ui-inspector/blob/80d9cff0ae15c40f1c5e5606b6beed66da6267ad/backend/README.md)
- [배포 안내](https://github.com/feed-mina/ui-inspector/blob/80d9cff0ae15c40f1c5e5606b6beed66da6267ad/backend/DEPLOY.md)
- [기존 쉬운 가이드](https://github.com/feed-mina/ui-inspector/blob/80d9cff0ae15c40f1c5e5606b6beed66da6267ad/docs/ui-inspector-sdui-easy-guide.html)
- [기존 수정 가이드](https://github.com/feed-mina/ui-inspector/blob/80d9cff0ae15c40f1c5e5606b6beed66da6267ad/docs/ui-inspector-sdui-fix-guide.html)
