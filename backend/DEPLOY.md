# 호스팅어 VPS 배포 — 핀 저장 창구

이 문서대로 하면 `https://inspector.mindevprofile.kr` 에서 창구가 열립니다.

> **상품을 먼저 확인하세요.** 호스팅어의 **VPS**(서버 한 대를 통째로 빌리는 상품)여야 합니다.
> 공유호스팅에서는 되지 않습니다 — 공유호스팅은 파이썬 앱을 옛 방식(WSGI)으로만 실행하고,
> FastAPI 가 쓰는 방식(ASGI)을 지원하지 않습니다.

주소는 키트 저장소 `studio/sdui-ui-inspector.js` 에 기본값으로 들어 있는 주소와 **같아야 합니다**.
다른 주소를 쓰시려면 그 한 줄도 함께 바꿔야 합니다.

## 먼저 — 이 서버가 비어 있습니까?

80·443 포트를 이미 누가 쓰고 있는지부터 봅니다. 길이 갈립니다.

```bash
ss -tlnp | grep -E ':80 |:443 '
```

| 결과 | 갈 길 |
|---|---|
| 아무것도 안 나옴 | **길 A** — 아래 1~11절 (systemd + Nginx + certbot) |
| `traefik`·`caddy`·`nginx`·`apache` 등이 잡고 있음 | **길 B** — 12절 (도커 컨테이너로 얹기). 1~11절은 건너뜁니다 |

길 B 인데 길 A 를 따라가면 **돌고 있는 서비스의 입구를 끊게 됩니다.** 80 포트는 하나뿐입니다.

| 무엇 | 값 |
|---|---|
| 바깥 주소 | `https://inspector.mindevprofile.kr` |
| 안쪽 포트 | `127.0.0.1:8001` (바깥에서 직접 닿지 않음) |
| 코드 위치 | `/opt/ui-inspector/app` |
| 파이썬 환경 | `/opt/ui-inspector/venv` |
| 장부 파일 | `/var/lib/ui-inspector/inspector.db` |
| 설정 파일 | `/etc/ui-inspector.env` |
| 서비스 이름 | `ui-inspector` |

포트를 8000 이 아니라 8001 로 쓰는 이유: 기존 EC2 에서 Django 가 8000 을 쓰고 있어서
(`gomgom-ai/server_log/장고랑워드프레스서버설정.md:60`), 나중에 한 서버로 합치더라도 겹치지 않게 하기 위해서입니다.

---

---

# 길 A — 빈 서버 (systemd + Nginx + certbot)

0~11절입니다. 80 포트를 이미 쓰는 것이 있다면 여기가 아니라 **12절**로 가세요.

## 0. 준비물

- 호스팅어 VPS 한 대 (Ubuntu 22.04 또는 24.04), `root` 로 SSH 접속 가능
- VPS 의 공인 IP 주소 하나 (호스팅어 관리 화면에 있습니다)
- `mindevprofile.kr` 의 DNS 를 고칠 수 있는 권한

아래 명령은 모두 **VPS 안에서** 실행합니다. `<VPS_IP>` 만 실제 값으로 바꾸세요.

---

## 1. 주소를 서버로 보낸다 (DNS)

도메인 관리 화면에서 A 레코드를 하나 추가합니다.

| 종류 | 이름 | 값 |
|---|---|---|
| A | `inspector` | `<VPS_IP>` |

확인 — 내 컴퓨터에서:

```bash
dig +short inspector.mindevprofile.kr
```

VPS 의 IP 가 나오면 됩니다. 바로 안 나오면 몇 분에서 몇 시간 기다립니다.
**이게 먼저 되어야 8번의 인증서 발급이 됩니다.**

---

## 2. 서버 기본 준비

```bash
apt update && apt -y upgrade
apt -y install python3-venv python3-pip nginx certbot python3-certbot-nginx git ufw
```

방화벽은 SSH 와 웹만 엽니다. 창구는 안쪽 주소로만 듣기 때문에 8001 은 열지 않습니다.

```bash
ufw allow OpenSSH
ufw allow 'Nginx Full'
ufw --force enable
ufw status
```

> Nginx 는 설치하는 순간 **부팅 시 자동 시작**으로 등록됩니다. 길 B 로 가기로 했다면
> 반드시 꺼 두세요. 안 그러면 다음 재부팅 때 Nginx 가 먼저 80 을 잡아
> 돌고 있던 서비스의 입구가 끊깁니다.
>
> ```bash
> systemctl disable --now nginx
> ```

---

## 3. 전용 사용자와 코드

서비스는 사람 계정이 아니라 전용 계정으로 돌립니다.

```bash
adduser --system --group --home /opt/ui-inspector uiinspector
mkdir -p /opt/ui-inspector /var/lib/ui-inspector
chown uiinspector:uiinspector /opt/ui-inspector /var/lib/ui-inspector

sudo -u uiinspector git clone https://github.com/feed-mina/ui-inspector.git /opt/ui-inspector/app
```

---

## 4. 파이썬 환경

```bash
sudo -u uiinspector python3 -m venv /opt/ui-inspector/venv
sudo -u uiinspector /opt/ui-inspector/venv/bin/pip install --upgrade pip
sudo -u uiinspector /opt/ui-inspector/venv/bin/pip install -r /opt/ui-inspector/app/backend/requirements.txt
```

확인:

```bash
/opt/ui-inspector/venv/bin/python -c "import fastapi, sqlalchemy; print(fastapi.__version__, sqlalchemy.__version__)"
```

---

## 5. 설정 파일

```bash
cat > /etc/ui-inspector.env <<'EOF'
INSPECTOR_DATABASE_URL=sqlite+pysqlite:////var/lib/ui-inspector/inspector.db
INSPECTOR_ALLOWED_ORIGINS=https://sdui-template-kit-productization.pages.dev
INSPECTOR_CREATE_TABLES=1
EOF
chown root:uiinspector /etc/ui-inspector.env
chmod 640 /etc/ui-inspector.env
```

- 장부 주소의 슬래시가 **네 개**인 것에 주의하세요. 세 개면 상대 경로로 읽힙니다.
- `INSPECTOR_CREATE_TABLES=1` 이면 서비스가 뜰 때 표가 없으면 만듭니다. SQLite 는 이게 가장 간단합니다.
  나중에 Postgres 로 옮길 때는 `backend/schema.sql` 로 사람이 만들고 이 값을 `0` 으로 둡니다.
- 허용 출처를 바꾸면 게시 화면에서 창구를 부를 수 없게 되니 그대로 두세요.

---

## 6. 서비스 등록

```bash
cat > /etc/systemd/system/ui-inspector.service <<'EOF'
[Unit]
Description=ui-inspector pins API
After=network.target

[Service]
Type=exec
User=uiinspector
Group=uiinspector
WorkingDirectory=/opt/ui-inspector/app/backend
EnvironmentFile=/etc/ui-inspector.env
ExecStart=/opt/ui-inspector/venv/bin/uvicorn app.main:app --host 127.0.0.1 --port 8001
Restart=on-failure
RestartSec=3
NoNewPrivileges=true
PrivateTmp=true
ProtectHome=true
ProtectSystem=strict
ReadWritePaths=/var/lib/ui-inspector

[Install]
WantedBy=multi-user.target
EOF

systemctl daemon-reload
systemctl enable --now ui-inspector
systemctl status ui-inspector --no-pager
```

`active (running)` 이 보여야 합니다. 확인:

```bash
curl -s http://127.0.0.1:8001/healthz
# {"ok":true,"data":{"status":"ok"},"errors":[]}
```

`ProtectSystem=strict` 때문에 이 서비스가 쓸 수 있는 곳은 `/var/lib/ui-inspector` 뿐입니다.
장부 위치를 옮기면 `ReadWritePaths` 도 같이 고쳐야 합니다.

---

## 7. 바깥 문 열기 (Nginx)

```bash
cat > /etc/nginx/sites-available/inspector <<'EOF'
server {
    listen 80;
    server_name inspector.mindevprofile.kr;

    location / {
        proxy_pass http://127.0.0.1:8001;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
EOF

ln -sf /etc/nginx/sites-available/inspector /etc/nginx/sites-enabled/inspector
nginx -t && systemctl reload nginx
```

이 서버를 이 창구 하나에만 쓰기 때문에 경로를 나누지 않고 `/` 전체를 넘깁니다.
나중에 같은 서버에 다른 것을 올리면 그때 `location /api/v1/inspector/` 로 좁히면 됩니다.

---

## 8. HTTPS

1번의 DNS 가 퍼진 뒤에 합니다.

```bash
certbot --nginx -d inspector.mindevprofile.kr
```

성공하면 Nginx 설정이 자동으로 443 을 쓰도록 바뀌고, 갱신은 시스템이 알아서 합니다.

```bash
systemctl status certbot.timer --no-pager
```

---

## 9. 확인

서버 바깥(내 컴퓨터)에서:

```bash
curl -s https://inspector.mindevprofile.kr/healthz
```

```bash
curl -s "https://inspector.mindevprofile.kr/api/v1/inspector/pins?url=https://example.com/&viewport=1280"
```

```bash
curl -s -X POST https://inspector.mindevprofile.kr/api/v1/inspector/pins \
  -H "Content-Type: application/json" \
  -d '{"url":"https://example.com/","viewport":1280,"pin":{"s":"#main > h1","ox":0.5,"oy":0.5,"fx":120,"fy":90,"text":"제목이 잘립니다","c":"layout"}}'
```

| 나와야 하는 것 | 뜻 |
|---|---|
| `{"ok":true,"data":{"status":"ok"},"errors":[]}` | 창구가 살아 있다 |
| `{"ok":true,"data":{"v":2,...,"pins":[]},"errors":[]}` | 목록 창구가 계약대로 답한다 |
| `{"ok":true,"data":{"id":1,"created":true},"errors":[]}` | 저장이 됐다 |

저장한 뒤 두 번째 명령을 다시 하면 방금 핀이 목록에 있어야 합니다.

**마지막은 눈으로** — 게시된 화면을 열고 아무 곳이나 눌러 핀을 찍고 댓글을 저장한 뒤
**새로고침**합니다. 핀이 남아 있으면 전부 이어진 것입니다.

### 안 될 때

| 증상 | 원인 | 할 일 |
|---|---|---|
| `502 Bad Gateway` | 창구가 안 떠 있다 | `journalctl -u ui-inspector -n 50` |
| `404` | Nginx 가 다른 곳을 보고 있다 | `nginx -t`, `server_name` 확인 |
| 인증서 발급 실패 | DNS 가 아직 안 퍼졌다 | 1번의 `dig` 를 다시 확인 |
| `unable to open database file` | 장부 폴더 권한 또는 `ReadWritePaths` | `ls -ld /var/lib/ui-inspector` |
| 게시 화면에서만 실패 | 허용 출처가 다르다 | `/etc/ui-inspector.env` 의 출처 확인 |
| 게시 화면에 "서버가 0 으로 응답" | 플러그인 기본 주소와 실제 주소가 다르다 | 키트의 `studio/sdui-ui-inspector.js` 기본값 확인 |

---

## 10. 평소 관리

```bash
# 로그 보기
journalctl -u ui-inspector -f

# 코드 갱신
sudo -u uiinspector git -C /opt/ui-inspector/app pull
sudo -u uiinspector /opt/ui-inspector/venv/bin/pip install -r /opt/ui-inspector/app/backend/requirements.txt
systemctl restart ui-inspector

# 되돌리기 (직전 상태로)
sudo -u uiinspector git -C /opt/ui-inspector/app checkout <이전 커밋>
systemctl restart ui-inspector

# 장부 백업 — 파일 하나를 복사하면 끝입니다
sqlite3 /var/lib/ui-inspector/inspector.db ".backup '/root/inspector-$(date +%F).db'"
```

---

## 11. 알아 두셔야 할 것

- **잠금장치가 없습니다.** 주소를 아는 사람은 누구나 핀을 넣고 볼 수 있습니다.
  북마클릿에 토큰을 심지 않는다는 저장소 원칙 때문에 창구도 인증을 요구하지 않습니다.
  공개 인터넷에 오래 두실 거라면 Nginx 기본 인증이나 사내망 제한을 앞에 두세요.
- **화면 내용은 받지 않습니다.** 들어오는 것은 선택자·좌표·사람이 직접 쓴 글뿐입니다.
- **장부가 파일 하나입니다.** 지금 쓰임에는 충분하지만, 사람이 많아지면
  `INSPECTOR_DATABASE_URL` 만 Postgres 주소로 바꾸면 됩니다. 코드는 그대로입니다.
- **핀 삭제와 답글 저장 창구는 아직 없습니다.** 표에는 자리가 있습니다.

---

# 길 B — 이미 Traefik 이 있는 서버에 얹기 (12절)

80·443 을 Traefik 이 쓰고 있으면 Nginx 로 포트를 뺏을 수 없습니다. 대신 Traefik 이
이미 하고 있는 일을 그대로 씁니다 — **라벨 붙인 컨테이너**로 얹으면 Traefik 이
경로도 HTTPS 인증서도 알아서 처리합니다. Traefik 의 설정이나 컨테이너는 건드리지 않습니다.

이 길에서는 1~11절 대신 아래만 하면 됩니다. `certbot` 도 필요 없습니다.

## 12-1. Traefik 구성 확인

```bash
docker ps --format '{{.Names}}'
docker inspect <traefik 컨테이너 이름> --format '{{json .Config.Cmd}}'
```

확인할 두 가지:

| 찾을 것 | 예 | 쓰는 곳 |
|---|---|---|
| HTTPS entrypoint 이름 | `--entrypoints.websecure.address=:443` → `websecure` | `compose.yaml` 의 `entrypoints` |
| 인증서 발급기 이름 | `--certificatesresolvers.letsencrypt.acme...` → `letsencrypt` | `compose.yaml` 의 `certresolver` |

`compose.yaml` 은 이 두 이름이 `websecure`·`letsencrypt` 인 경우로 적혀 있습니다.
다르면 그 두 줄만 바꿉니다.

## 12-2. DNS

1절과 같습니다. A 레코드 `inspector` → 서버 IP.
Traefik 의 인증서 발급은 HTTP 챌린지라, **DNS 가 퍼진 뒤에야** 인증서가 나옵니다.

## 12-3. 올리기

```bash
git clone https://github.com/feed-mina/ui-inspector.git /opt/ui-inspector/app
cd /opt/ui-inspector/app/backend
docker compose up -d --build
docker compose ps
```

`ui-inspector-pins` 가 `running (healthy)` 가 되면 됩니다.
`healthy` 까지 10~40초쯤 걸립니다.

## 12-4. 확인

컨테이너 안에서:

```bash
docker compose exec pins python -c "import urllib.request; print(urllib.request.urlopen('http://127.0.0.1:8001/healthz').read().decode())"
```

바깥에서(9절과 같은 명령):

```bash
curl -s https://inspector.mindevprofile.kr/healthz
```

## 12-5. 안 될 때

| 증상 | 원인 | 할 일 |
|---|---|---|
| 바깥에서 404 | Traefik 이 라벨을 못 읽었다 | `docker compose config --format json` 로 라벨 확인, `docker logs <traefik>` |
| 인증서 오류 | DNS 가 아직 안 퍼졌다 | `dig +short inspector.mindevprofile.kr` |
| `unhealthy` | 창구가 안 떴다 | `docker compose logs pins` |
| 컨테이너는 도는데 Traefik 이 못 닿음 | Traefik 이 다른 네트워크만 본다 | 라벨에 `traefik.docker.network` 를 더한다 |

## 12-6. 평소 관리

```bash
cd /opt/ui-inspector/app
git pull
cd backend && docker compose up -d --build     # 갱신
docker compose logs -f pins                    # 로그
docker compose down                            # 내리기 (장부는 볼륨에 남는다)

# 장부 백업
docker run --rm -v ui-inspector_pins-data:/data -v "$PWD":/out alpine \
  cp /data/inspector.db /out/inspector-$(date +%F).db
```

길 A 의 systemd 서비스를 먼저 만들어 두셨다면, 둘이 같이 돌 필요가 없으니 끄세요.

```bash
systemctl disable --now ui-inspector
```
