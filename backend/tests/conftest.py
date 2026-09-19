import os
import sys
from pathlib import Path

# app 을 import 하기 전에 정해야 한다. 테스트는 아래 fixture 의 엔진만 쓰므로
# 앱이 기본 DB 파일을 만들지 않게 막는다.
os.environ.setdefault("INSPECTOR_DATABASE_URL", "sqlite+pysqlite:///:memory:")
os.environ.setdefault("INSPECTOR_CREATE_TABLES", "0")

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.pool import StaticPool

BACKEND_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BACKEND_ROOT))

from app.db import metadata  # noqa: E402
from app.main import app, get_connection  # noqa: E402

REPO_ROOT = BACKEND_ROOT.parent
CONTRACT_DIR = REPO_ROOT / "sdui" / "ui-inspector" / "contracts"
MANIFEST_PATH = REPO_ROOT / "sdui" / "ui-inspector" / "template.manifest.json"


@pytest.fixture()
def engine():
    """테스트마다 빈 메모리 SQLite. 표는 app/db.py 의 정의로 만든다."""
    test_engine = create_engine(
        "sqlite+pysqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
        future=True,
    )
    metadata.create_all(test_engine)
    yield test_engine
    test_engine.dispose()


@pytest.fixture()
def client(engine):
    """창구를 그 엔진에 연결한다."""

    def override():
        with engine.begin() as connection:
            yield connection

    app.dependency_overrides[get_connection] = override
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()
