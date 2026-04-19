# Telegram Channel Analytics MVP

## Project Overview

Telegram Channel Analytics MVP is a containerized web application for collecting and viewing analytics from public Telegram channels. It uses a Telegram user session through `Telethon`, fetches recent channel posts, stores them in `PostgreSQL`, calculates a simple popularity signal, exposes data through a `FastAPI` backend, and shows the result in a `Next.js` frontend.

The project was built as a practical final project for a cloud and container deployment course. It is intentionally MVP-sized: simple, runnable, and easy to explain during a defence.

## Current Live Deployment

Current Oracle Cloud deployment:

```text
Frontend: http://144.24.168.76:3000
Backend health: http://144.24.168.76:8000/health
```

This IP is an Oracle Cloud ephemeral public IP. If the VM is recreated or the public IP changes, update the URLs in `.env`, Oracle Cloud security rules, and this README.

## What The App Does

- Tracks configured public Telegram channels.
- Fetches channel history through `Telethon` using a Telegram user session.
- Stores posts, views, forwards, replies, reactions, dates, and calculated metrics in `PostgreSQL`.
- Calculates a simple early popularity signal based on channel median views.
- Runs manual sync through an API endpoint.
- Runs periodic background sync through `APScheduler`.
- Provides REST endpoints for channels, health, sync, and posts.
- Shows channels and posts in a browser-friendly frontend designed to also fit Telegram Mini App usage.

## Architecture

```text
Telegram public channels
        |
        | Telethon user session
        v
FastAPI backend
        |
        | SQLAlchemy + Alembic
        v
PostgreSQL
        ^
        |
Next.js frontend
```

The backend owns Telegram integration, database access, analytics, API routes, migrations, and scheduler jobs. The frontend only calls public backend endpoints and does not contain secrets.

## Tech Stack

- Backend: `Python 3.12`, `FastAPI`, `SQLAlchemy 2.x`, `Alembic`, `Telethon`, `APScheduler`, `Pydantic settings`, `uvicorn`
- Frontend: `Next.js App Router`, `TypeScript`, CSS
- Database: `PostgreSQL`
- Infra: `Docker`, `Docker Compose`
- Cloud deployment used for final demo: `Oracle Cloud Free Tier VM`

## Repository Structure

```text
.
├── backend/
│   ├── alembic/                 database migrations
│   ├── app/
│   │   ├── api/                 FastAPI routes
│   │   ├── core/                settings and logging
│   │   ├── db/                  SQLAlchemy session and metadata
│   │   ├── models/              database models
│   │   ├── scheduler/           APScheduler setup
│   │   ├── schemas/             API response schemas
│   │   ├── services/            Telegram sync and business logic
│   │   └── utils/               metrics and time helpers
│   ├── scripts/                 Telethon session bootstrap script
│   ├── Dockerfile
│   └── requirements.txt
├── frontend/
│   ├── app/                     Next.js App Router pages
│   ├── components/              UI components
│   ├── lib/                     API client, types, format helpers
│   ├── public/
│   ├── Dockerfile
│   └── package.json
├── docs/                        final report document
├── docker-compose.yml
└── README.md
```

## API Endpoints

```text
GET  /health
GET  /api/channels
POST /api/sync
GET  /api/posts/top?period=7d|30d|90d|all&limit=20
GET  /api/posts/recent?limit=20
```

For the current demo, the frontend reads from `/api/posts/top`, while the backend returns the newest stored posts with analytics fields. Use `period=all` when you want to see all synced posts regardless of age.

## Database Tables

`tracked_channels`

- `id`
- `username`
- `title`
- `is_active`
- `created_at`
- `updated_at`

`channel_posts`

- `id`
- `tracked_channel_id`
- `telegram_message_id`
- `message_date`
- `text`
- `views`
- `forwards`
- `replies_count`
- `reactions_total`
- `channel_median_views`
- `alert_threshold_views`
- `popularity_score`
- `is_alert_candidate`
- `alerted_at`
- `collected_at`
- `raw_json`
- `created_at`
- `updated_at`

There is a uniqueness constraint on:

```text
tracked_channel_id + telegram_message_id
```

This allows safe upserts when the same post is synced again with newer metrics.

## Analytics Logic

The MVP uses a simple non-ML rule:

```text
lookback period: 90 days
early window: 8 hours after publication
threshold: 50% of the channel median views
```

A post is marked as an alert candidate when:

```text
post_age <= 8 hours
views >= channel_median_views * 0.5
```

The `popularity_score` shows how strongly the post performs against the threshold:

```text
popularity_score = views / alert_threshold_views * 100
```

Example:

```text
channel median views: 100000
alert threshold: 50000
post views: 75000
popularity_score: 150
```

Reactions, forwards, and replies are stored and shown, but the current alert signal mainly uses views because view count is the most consistently available metric across public Telegram channels.

## Required Credentials

The backend needs:

```text
TELEGRAM_API_ID
TELEGRAM_API_HASH
TELEGRAM_PHONE
TELETHON_SESSION_NAME
```

Get `TELEGRAM_API_ID` and `TELEGRAM_API_HASH` from:

```text
https://my.telegram.org
```

Do not hardcode these values in source code.

Do not put Telegram secrets, bot tokens, or session files into frontend code.

The frontend should only contain public configuration:

```text
NEXT_PUBLIC_API_BASE_URL
```

## Secret Files

These files are local/server-only and must not be committed:

```text
.env
backend/.env
frontend/.env.local
backend/sessions/*.session
*.session
```

Before pushing, check:

```bash
git status --ignored
```

Secrets and session files should appear as ignored files, not staged files.

## Local Setup

Create a root `.env` file:

```env
APP_ENV=development
APP_HOST=0.0.0.0
APP_PORT=8000

TELEGRAM_API_ID=your_api_id
TELEGRAM_API_HASH=your_api_hash
TELEGRAM_PHONE=+your_phone_number

TELETHON_SESSION_NAME=telegram_user
TELETHON_SESSION_HOST_DIR=C:/telegram_analytics_sessions

TELEGRAM_CHANNELS=tproger,habr_com
SYNC_INTERVAL_MINUTES=120
FETCH_LIMIT=30
TELEGRAM_REQUEST_PAUSE_SECONDS=3

CORS_ORIGINS=http://localhost:3000
NEXT_PUBLIC_API_BASE_URL=http://localhost:8000
```

Create the Telethon session locally:

```bash
cd backend
python -m pip install -r requirements.txt
python scripts/create_telethon_session.py
```

The script asks for the Telegram login code and, if enabled, the 2FA password. After successful login, a session file is created.

Start the whole project:

```bash
docker compose up -d --build
```

Check containers:

```bash
docker compose ps
```

Check backend:

```bash
curl http://localhost:8000/health
```

Trigger sync:

```bash
curl -X POST http://localhost:8000/api/sync
```

Open frontend:

```text
http://localhost:3000
```

## Oracle Cloud Deployment

The current deployment uses an Oracle Cloud Free Tier VM:

```text
OS: Ubuntu 22.04
Shape used: VM.Standard.E2.1.Micro
Public IP: 144.24.168.76
```

Basic server setup:

```bash
sudo apt update
sudo apt install -y git curl ca-certificates
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo apt install -y docker-compose-plugin
docker --version
docker compose version
```

Clone the repo:

```bash
git clone https://github.com/maskadok/telegram_channels
cd telegram_channels
```

Create server `.env`:

```bash
nano .env
```

Server `.env` example:

```env
APP_ENV=production
APP_HOST=0.0.0.0
APP_PORT=8000

TELEGRAM_API_ID=your_api_id
TELEGRAM_API_HASH=your_api_hash
TELEGRAM_PHONE=+your_phone_number

TELETHON_SESSION_NAME=telegram_user
TELETHON_SESSION_HOST_DIR=/opt/telegram_analytics_sessions

TELEGRAM_CHANNELS=tproger,habr_com
SYNC_INTERVAL_MINUTES=120
FETCH_LIMIT=30
TELEGRAM_REQUEST_PAUSE_SECONDS=3

CORS_ORIGINS=http://144.24.168.76:3000
NEXT_PUBLIC_API_BASE_URL=http://144.24.168.76:8000
```

Create the session directory:

```bash
sudo mkdir -p /opt/telegram_analytics_sessions
sudo chown -R ubuntu:ubuntu /opt/telegram_analytics_sessions
chmod 700 /opt/telegram_analytics_sessions
```

Copy the local session file from Windows to the server:

```powershell
scp -i "C:\Users\maska\.ssh\ssh-key-2026-04-19.key" "C:\telegram_analytics_sessions\telegram_user.session" ubuntu@144.24.168.76:/opt/telegram_analytics_sessions/telegram_user.session
```

Start the project on the server:

```bash
sudo docker compose up -d --build
```

Check it:

```bash
sudo docker compose ps
curl http://localhost:8000/health
curl -X POST http://localhost:8000/api/sync
curl "http://localhost:8000/api/posts/top?period=all&limit=3"
```

## Oracle Cloud Network Rules

For the current public demo, Oracle Cloud ingress rules must allow:

```text
TCP 22    from your IP, for SSH
TCP 3000  from 0.0.0.0/0, for frontend
TCP 8000  from 0.0.0.0/0, for backend API
```

If `localhost` works on the server but `http://SERVER_IP:3000` or `http://SERVER_IP:8000/health` times out from your browser, the problem is usually Oracle networking/security rules.

## Verification Checklist

Backend health:

```bash
curl http://localhost:8000/health
```

Expected result includes:

```json
{
  "status": "ok",
  "database": "ok",
  "scheduler_running": true
}
```

Manual sync:

```bash
curl -X POST http://localhost:8000/api/sync
```

Expected result:

```json
{
  "channels_processed": 2,
  "errors": []
}
```

Posts endpoint:

```bash
curl "http://localhost:8000/api/posts/top?period=all&limit=3"
```

Frontend:

```text
http://localhost:3000
http://144.24.168.76:3000
```

## Common Problems

`telethon session is not authorized`

The backend cannot use a valid Telegram session. Create the session with `python scripts/create_telethon_session.py` and make sure the `.session` file is mounted into `/app/sessions` in Docker.

`ApiIdInvalidError`

`TELEGRAM_API_ID` and `TELEGRAM_API_HASH` do not match. Recheck them at `my.telegram.org`.

Browser cannot open public IP

Check Oracle Cloud ingress rules for ports `3000` and `8000`.

Frontend is empty

Run manual sync:

```bash
curl -X POST http://localhost:8000/api/sync
```

Then use:

```text
period=all
```

Docker Compose starts but backend fails

Check logs:

```bash
sudo docker compose logs --tail=120 backend
```

Telegram flood wait

Reduce sync frequency, reduce `FETCH_LIMIT`, and track fewer channels.

## Telegram Mini App Notes

The frontend is designed to be usable inside Telegram WebApp and in a normal browser. For a proper Telegram Mini App production setup, use:

```text
HTTPS frontend URL
BotFather Mini App configuration
No frontend secrets
```

For the current university demo, the public browser URL is enough to show a working cloud deployment. Telegram Mini App HTTPS polish can be done later.

## Security Notes

The most sensitive file is the Telethon `.session` file. If it leaks, someone may be able to access the Telegram account session without a one-time login code.

If secrets leak:

1. Delete leaked `.session` files locally and from the server.
2. Terminate suspicious Telegram sessions in Telegram settings.
3. Generate a new Telethon session.
4. Consider creating new Telegram API credentials.
5. Check Git history for accidental secret commits.

## MVP Limitations

- Only configured channels are tracked.
- Private channels require the Telegram user account to have access.
- Metrics depend on what Telegram exposes to the user account.
- The analytics rule is simple and does not use ML.
- The current public deployment uses HTTP ports `3000` and `8000`, not a hardened HTTPS reverse proxy.
- This is an MVP, not a production-hardened system.

## Final Project Defence Checklist

Prepare these items:

- GitHub repository link.
- Public frontend URL.
- Backend health URL.
- Screenshot of Oracle Cloud VM running.
- Screenshot of `docker compose ps`.
- Screenshot of frontend with Telegram posts.
- Screenshot of `/health`.
- Screenshot or terminal output of `/api/sync`.
- Short report in `docs/Final_Project_Report.docx`.

