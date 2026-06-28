# tech‑spec.md – laser‑drone‑target (v1)

---

## 1. Stack  

| Layer | Technology | Version | Rationale |
|-------|------------|---------|-----------|
| **Language** | Python | 3.11 | Mature ecosystem for computer‑vision, sensor fusion, and rapid prototyping. |
| **Web framework** | FastAPI | 0.110.0 | Async‑first, OpenAPI auto‑gen, easy JWT integration. |
| **Drone middleware** | ROS 2 (Foxy) | 0.10.0 | Industry‑standard for UAV control, supports hardware‑agnostic topics. |
| **Computer‑vision / sensor fusion** | OpenCV + PyTorch | 4.9.0 / 2.3.0 | Real‑time image processing + optional DL model for target classification. |
| **Inertial navigation** | RTK‑IMU library (`pyimu`) | 1.2.1 | Provides high‑rate IMU data & sensor‑fusion filters (Mahony/Madgwick). |
| **Message bus** | MQTT (Eclipse Mosquitto) | 2.0.15 | Low‑latency telemetry between drone and backend. |
| **Database** | PostgreSQL (via SQLModel) | 15 | Relational, ACID, free‑tier on Supabase/AWS RDS. |
| **Container runtime** | Docker | 24.0.5 | Guarantees reproducible environment across dev / prod. |
| **Orchestration (dev)** | Docker‑Compose | 2.24.5 | Simple multi‑service local dev stack. |
| **Observability** | Prometheus + Grafana, OpenTelemetry, Loguru | – | Standardised metrics & tracing. |

---

## 2. Hosting (Free‑Tier‑First)

| Component | Preferred Provider (Free Tier) | Alternative | Deployment notes |
|-----------|--------------------------------|-------------|------------------|
| **API / FastAPI** | Fly.io (free‑tier 3‑CPU‑hours/month) | Render.com (free web service) | Deploy as a Docker container; auto‑scale to 1‑vCPU, 256 MiB RAM. |
| **PostgreSQL** | Supabase (free 500 MB) | AWS RDS Free Tier (t2.micro) | Use Supabase managed DB; enable Row‑Level Security (RLS). |
| **MQTT broker** | CloudMQTT (free 10 connections) | Eclipse Mosquitto on Fly.io (single‑node) | TLS‑enabled, password auth. |
| **Prometheus / Grafana** | Grafana Cloud (free 50 k samples/sec) | Self‑hosted on Fly.io (small VM) | Scrape `/metrics` endpoint of FastAPI. |
| **Static assets (docs, UI)** | GitHub Pages (free) | Netlify (free tier) | Serve OpenAPI UI (`/docs`) and simple React front‑end. |
| **CI/CD** | GitHub Actions (free minutes) | – | Build → test → push Docker image → Fly.io deploy. |

*All secrets stored in provider‑specific secret stores (Fly.io secrets, GitHub Envs, Supabase `service_role`).*

---

## 3. Data Model  

| Table / Collection | Key Fields | Description |
|--------------------|------------|-------------|
| **users** | `id (UUID PK)`, `email (unique)`, `hashed_pw`, `role (enum: admin, operator, analyst)` | Auth‑principal. |
| **missions** | `id (UUID PK)`, `owner_id (FK → users)`, `name`, `status (enum: draft, active, completed, aborted)`, `created_at`, `updated_at` | High‑level mission metadata. |
| **targets** | `id (UUID PK)`, `mission_id (FK)`, `timestamp`, `lat`, `lon`, `alt_m`, `confidence (0‑1)`, `image_url (optional)` | Each computed target coordinate. |
| **sensor_logs** | `id (UUID PK)`, `mission_id (FK)`, `type (enum: imu, lidar, camera)`, `payload (JSONB)`, `ts` | Raw telemetry for post‑flight analysis. |
| **api_keys** | `key (string PK)`, `owner_id (FK)`, `scopes (JSON)`, `created_at`, `revoked_at` | Service‑to‑service auth (e.g., external command‑&‑control). |

*Indexes:* `missions.owner_id`, `targets.mission_id + ts`, `sensor_logs.mission_id + type + ts`.

---

## 4. API Surface  

| Method | Path | Purpose | Request Body (JSON) | Response |
|--------|------|---------|---------------------|----------|
| **POST** | `/auth/login` | Issue JWT for user/password | `{email, password}` | `{access_token, token_type:"bearer", expires_in}` |
| **POST** | `/missions` | Create a new mission (draft) | `{name}` | `{mission_id, status}` |
| **GET** | `/missions/{mission_id}` | Retrieve mission details + status | – | Mission object + list of target IDs |
| **POST** | `/missions/{mission_id}/activate` | Switch mission to *active* → starts MQTT subscription | – | `{status:"active"}` |
| **POST** | `/missions/{mission_id}/targets` | Manually submit a target (fallback) | `{lat, lon, alt_m, confidence, image_url?}` | `{target_id}` |
| **GET** | `/missions/{mission_id}/targets` | List computed targets (paginated) | `?page=&size=` | `{items:[...], total, page, size}` |
| **GET** | `/missions/{mission_id}/sensor-logs` | Stream raw sensor logs (CSV or NDJSON) | `?type=imu|camera|lidar` | `application/octet-stream` |
| **GET** | `/healthz` | Liveness / readiness probe | – | `200 OK` + JSON `{status:"ok"}` |
| **GET** | `/metrics` | Prometheus metrics endpoint | – | `text/plain` |
| **POST** | `/admin/api-keys` *(admin only)* | Create API key for external systems | `{owner_id, scopes}` | `{api_key, created_at}` |

*All non‑public endpoints require Bearer JWT (HS256) or valid API‑Key header (`x-api-key`).*

---

## 5. Security Model  

| Aspect | Implementation |
|--------|----------------|
| **Authentication** | FastAPI OAuth2PasswordBearer with JWT signed by HS256 secret (`JWT_SECRET`). Tokens expire in 1 h; refresh via `/auth/refresh` (optional). |
| **Authorization** | Role‑based (RBAC) checks via dependency injection. `admin` can manage users & API keys; `operator` can create/activate missions; `analyst` read‑only. |
| **Transport security** | All inbound/outbound traffic forced TLS (HTTPS). MQTT broker uses TLS with client‑certs (optional) + username/password. |
| **Secret management** | - `JWT_SECRET`, DB password, MQTT credentials stored in provider secret store (Fly.io secrets). <br> - Docker build uses `--build-arg` for compile‑time secrets; never baked into image. |
| **Database security** | - Row‑Level Security (RLS) policies enforce `owner_id = current_user_id`. <br> - Enforce `sslmode=require` on PostgreSQL connections. |
| **API key security** | API keys are 32‑byte base64 strings, stored hashed (bcrypt) in `api_keys`. Scopes restrict allowed endpoints. |
| **Supply‑chain** | Base Docker image `python:3.11-slim` pinned by digest. All third‑party wheels verified via `pip hash`. |
| **Compliance** | No PII stored; only operational telemetry. Aligns with ITAR‑friendly handling (no export‑controlled data). |

---

## 6. Observability  

| Category | Tool / Integration | Details |
|----------|-------------------|---------|
| **Logging** | Loguru → JSON stdout | Structured fields: `request_id`, `user_id`, `mission_id`, `level`, `msg`. Collected by Fly.io logs (forwarded to Grafana Loki). |
| **Metrics** | Prometheus client (`prometheus_fastapi_instrumentator`) | Built‑in counters: `http_requests_total`, `mission_active`, `target_generated`, `sensor_msg_received`. Exported at `/metrics`. |
| **Dashboards** | Grafana Cloud | Pre‑built dashboards for mission health, latency, error rates. |
| **Tracing** | OpenTelemetry SDK → OTLP exporter → Grafana Tempo | End‑to‑end trace across API, MQTT consumer, ROS node. |
| **Alerting** | Grafana alerts → Slack webhook | Thresholds: API 5xx > 1 % over 5 min, mission activation failures > 3/min, CPU > 80 % for >2 min. |
| **Health checks** | `/healthz` (liveness) & `/readyz` (dependency check) | Kubernetes‑style probes (if later moved to k8s). |

---

## 7. Build / CI  

**GitHub Actions workflow (`.github/workflows/ci.yml`)**

```yaml
name: CI / CD

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  lint-test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: "3.11"
      - name: Cache pip
        uses: actions/cache@v3
        with:
          path: ~/.cache/pip
          key: pip-${{ hashFiles('pyproject.toml') }}
      - name: Install deps
        run: pip install -r requirements.txt
      - name: Lint
        run: ruff check .
      - name: Type check
        run: mypy .
      - name: Unit tests
        run: pytest -q --cov=app
      - name: Build Docker image
        run: |
          docker build -t ghcr.io/${{ github.repository }}:sha-${{ github.sha }} .
      - name: Push image (if main)
        if: github.ref == 'refs/heads/main'
        uses: docker/login-action@v3
        with:
          registry: ghcr.io
          username: ${{ github.actor }}
          password: ${{ secrets.GITHUB_TOKEN }}
      - name: Push Docker
        if: github.ref == 'refs/heads/main'
        run: |
          docker push ghcr.io/${{ github.repository }}:sha-${{ github.sha }}
      - name: Deploy to Fly.io
        if: github.ref == 'refs/heads/main'
        uses: superfly/flyctl-actions@v1
        with:
          args: "deploy --image ghcr.io/${{ github.repository }}:sha-${{ github.sha }}"
        env:
          FLY_API_TOKEN: ${{ secrets.FLY_API_TOKEN }}
```

*Key points*  

- **Static analysis**: `ruff` (lint) + `mypy` (type).  
- **Test coverage**: Minimum 80 % required; fails CI otherwise.  
- **Docker**: Multi‑stage build; final stage copies only `app/` and compiled wheels.  
- **Secrets**: `FLY_API_TOKEN`, `JWT_SECRET`, DB credentials stored as GitHub repo secrets.  
- **Deploy**: Fly.io `flyctl` automatically rolls out new version; zero‑downtime via rolling release.  

--- 

*End of technical specification.*