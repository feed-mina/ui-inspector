# 핀 저장 창구 (FastAPI)

SDUI 게시 화면의 댓글 패널이 핀을 저장하고 불러오는 서버입니다.
계약은 이미 저장소에 있는 `sdui/ui-inspector/contracts/*.schema.json` 이고,
그 계약의 정본은 `src/state.js` 의 `validateState`(스키마 버전 2)입니다.

| 창구 | 부르는 쪽 |
|---|---|
| `GET /api/v1/inspector/pins?url=&viewport=` | hydrator `inspector.pins.list` |
| `POST /api/v1/inspector/pins` | action `inspector.pins.save` |
| `GET /healthz` | 배포 점검용 |

부르는 쪽은 SDUI 키트 저장소의 `studio/sdui-ui-inspector.js` 입니다.
키트가 만드는 게시 페이지에는 `<meta>` 를 넣을 자리가 없어서, 그 파일에 기본 주소
`https://inspector.feedmina.tech` 가 들어 있습니다. **이 창구를 올리는 주소가 그 값과 같아야 합니다.**

응답 봉투는 키트 표준 `{ "ok": ..., "data": ..., "errors": [] }` 입니다.
`data.v` 는 항상 `2` 입니다. 다른 값이면 북마클릿의 `validateState` 가 상태 전체를 버립니다.

## 띄우기

```bash
cd backend
python -m venv .venv && . .venv/bin/activate     # 윈도우: .venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --port 8000
```

DB 를 정하지 않으면 `./inspector.db` (SQLite) 가 만들어집니다. 혼자 확인할 때만 쓰세요.

서버에 올리는 순서는 [`DEPLOY.md`](./DEPLOY.md) 에 있습니다(호스팅어 VPS 기준,
DNS·systemd·Nginx·HTTPS·확인 명령까지).

## 환경 변수

| 이름 | 기본값 | 뜻 |
|---|---|---|
| `INSPECTOR_DATABASE_URL` | `sqlite+pysqlite:///./inspector.db` | 운영은 `postgresql+psycopg2://user:pw@host:5432/inspector` |
| `INSPECTOR_ALLOWED_ORIGINS` | `https://sdui-template-kit-productization.pages.dev` | 쉼표로 여러 개. 여기 없는 주소에서 온 호출에는 CORS 헤더를 주지 않습니다 |
| `INSPECTOR_CREATE_TABLES` | `1` | 뜰 때 표가 없으면 만듭니다. 운영에서는 `schema.sql` 로 사람이 만들고 `0` 으로 둡니다 |

## DB

표 두 개뿐입니다. `schema.sql` 이 Postgres 기준 정본이고,
`app/db.py` 가 같은 표를 SQLAlchemy 로 적은 것입니다.

| 표 | 담는 것 |
|---|---|
| `inspector_pins` | 핀 한 건. 조회키 `selector`(=`pin.s`)와 저장 데이터 `fallback_x`/`fallback_y`/`body` 를 분리 |
| `inspector_pin_replies` | 답글. 핀이 지워지면 같이 지워집니다 |

```bash
psql "$INSPECTOR_DATABASE_URL" -f schema.sql
```

## 눈으로 확인

```bash
curl -s "http://localhost:8000/api/v1/inspector/pins?url=https://example.com/&viewport=1280"

curl -s -X POST http://localhost:8000/api/v1/inspector/pins -H "Content-Type: application/json" \
  -d '{"url":"https://example.com/","viewport":1280,"pin":{"s":"#main > h1","ox":0.5,"oy":0.5,"fx":120,"fy":90,"text":"제목이 잘립니다","c":"layout"}}'
```

첫 명령은 `{"ok":true,"data":{"v":2,...,"pins":[]},"errors":[]}`,
두 번째는 `{"ok":true,"data":{"id":1,"created":true},"errors":[]}` 를 돌려주고,
다시 첫 명령을 하면 방금 핀이 목록에 있습니다.

## 시험

```bash
pip install -r requirements-dev.txt
pytest
```

`tests/test_contract.py` 는 실제 요청·응답을 `sdui/ui-inspector/contracts/` 의
JSON Schema 로 검사하고, 필수 필드·카테고리 목록·길이 한도가 서버와 계약에서
같은 값인지도 봅니다. 여기서 깨지면 대개 고쳐야 하는 쪽은 서버입니다.

## 규칙

- **화면 내용을 받지 않습니다.** 들어오는 것은 선택자·좌표·사람이 직접 쓴 글뿐입니다.
  대상 페이지의 텍스트나 HTML 은 계약에 아예 없습니다.
- **토큰이 없습니다.** 북마클릿에 토큰을 심지 않는다는 저장소 원칙 때문에
  이 창구도 인증을 요구하지 않습니다. 공개망에 그대로 두지 말고,
  사내망이나 앞단 인증 뒤에 두세요. 로그인을 붙이는 일은 아직 하지 않았습니다.
- **핀 삭제·답글 저장 창구는 아직 없습니다.** 표에는 자리가 있고 목록 응답에도
  실리지만, 쓰는 쪽 창구는 만들지 않았습니다.
