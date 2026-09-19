# 핀 저장 창구 이미지.
#
# 이미 Traefik 이 80·443 을 쓰고 있는 서버용이다. 그런 서버에서는 Nginx 로
# 포트를 뺏을 수 없으므로, 돌고 있는 다른 서비스들과 같은 방식(라벨 붙인
# 컨테이너)으로 얹는다. 빈 서버라면 DEPLOY.md 의 길 A(systemd + Nginx)를 쓴다.
#
# 빌드 기준 폴더는 이 폴더(backend/)다.
FROM python:3.12-slim

ENV PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    INSPECTOR_DATABASE_URL=sqlite+pysqlite:////var/lib/ui-inspector/inspector.db

WORKDIR /app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY app ./app

# 장부를 담을 곳. compose 가 여기에 볼륨을 건다.
RUN useradd --system --uid 10001 --user-group uiinspector \
 && mkdir -p /var/lib/ui-inspector \
 && chown uiinspector:uiinspector /var/lib/ui-inspector
USER uiinspector

EXPOSE 8001

# 바깥에 포트를 열지 않는다. Traefik 이 컨테이너 주소로 직접 닿는다.
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
  CMD ["python", "-c", "import urllib.request,sys; sys.exit(0 if urllib.request.urlopen('http://127.0.0.1:8001/healthz', timeout=4).status == 200 else 1)"]

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8001"]
