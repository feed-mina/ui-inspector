"""환경 변수로만 바뀌는 설정. 기본값은 로컬에서 바로 띄울 수 있는 값이다."""

import os

# 기본값은 파일 SQLite. 운영에서는 Postgres 주소를 넣는다.
#   INSPECTOR_DATABASE_URL=postgresql+psycopg2://user:pw@host:5432/inspector
DATABASE_URL = os.environ.get("INSPECTOR_DATABASE_URL", "sqlite+pysqlite:///./inspector.db")

# 게시된 SDUI 화면에서만 호출할 수 있게 막는다.
# 플러그인(키트 studio/sdui-ui-inspector.js)이 이 주소에서 fetch 한다.
DEFAULT_ORIGINS = "https://sdui-template-kit-productization.pages.dev"
ALLOWED_ORIGINS = [
    origin.strip()
    for origin in os.environ.get("INSPECTOR_ALLOWED_ORIGINS", DEFAULT_ORIGINS).split(",")
    if origin.strip()
]

# 앱이 뜰 때 표가 없으면 만들지 여부. 운영에서는 schema.sql 로 사람이 만들고 0 으로 둔다.
CREATE_TABLES = os.environ.get("INSPECTOR_CREATE_TABLES", "1") not in ("0", "false", "False")
