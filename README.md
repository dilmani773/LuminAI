# LuminAI

AI-powered maternal healthcare assistant for Sri Lanka. HackElite 3.0 project — Team Pulse 404.

## Project structure

```
luminai/
├── backend/       # FastAPI + Postgres + AI agents 
├── mobile_app/    # Flutter app for mothers 
├── dashboard/     # React dashboard for PHMs/doctors 
├── data/          # RAG source data (Sri Lankan foods, MOH guidelines)
├── infra/         # docker-compose, deployment config
└── docs/          # database_schema, api_contract - READ THESE before building
```

Read `docs/database_schema.md` and `docs/api_contract.md` first — they define
every field name and endpoint your part will talk to. If something there
needs to change, raise it in the group chat before building against it.

## Running the backend locally (everyone needs this working)

**Prerequisite: Docker Desktop must be installed AND running.**
Download: https://www.docker.com/products/docker-desktop/
After installing, open the Docker Desktop app itself and wait until it shows
"running" (whale icon steady in system tray / menu bar). `docker --version`
only checks the CLI is installed — it does NOT mean the engine is running.

```bash
git clone <repo-url>
cd LuminAI/infra
docker compose up --build
```

Wait for both `postgres-1` and `backend-1` logs to appear, ending with
`Application startup complete`. Then open:

```
http://localhost:8000/docs
```

You should see the FastAPI docs page. That means Postgres + backend are both
running and talking to each other, and all database tables have been created
automatically.

**Do not run the backend outside Docker** (no local venv/pip install) unless
you have a specific reason to — see Troubleshooting below for why.

## Troubleshooting

**`unable to get image... dockerDesktopLinuxEngine`**
Docker Desktop app isn't actually running, only the CLI is installed. Open
the Docker Desktop application and wait for it to fully start, then retry.

**`Microsoft Visual C++ 14.0 or greater is required` (psycopg2-binary)**
Only happens if you try installing Python packages locally (outside Docker)
on Windows with a newer Python version. Don't do this — use Docker instead,
it avoids this entirely since it builds on Linux internally.

**`password authentication failed for user "luminai"`**
Means the backend is trying to connect to a Postgres that isn't the Docker
one (e.g. you ran it locally without Docker, or have a stray local Postgres
on port 5432). Stick to running everything through `docker compose up`.

**`ImportError: cannot import name 'X' from 'app.models.y'`**
A filename or class name typo somewhere in `app/models/`. Check that the
filename, the class name inside it, and the import line in `models/__init__.py`
all match exactly (case-sensitive, including things like `appointment` not
`apointment`).

**Made a code change and don't see it reflected?**
The Docker setup uses `--reload`, so changes to backend code auto-reload. If
you added a brand new file/folder or changed `requirements.txt`, stop
(`Ctrl+C`) and rerun `docker compose up --build` to pick it up properly.

## Status

- ✅ Database models (10 tables) — done
- ✅ Docker + Postgres setup — done
- ✅ Schema + API contract docs — done
- 🔜 Auth (register/login for PHM, Mother, Doctor)
- ⬜ CRUD routers (mothers, appointments, reports, monitoring, meal plans, symptom logs, alerts)
- ⬜ 3 AI agents (Report Analysis, Nutritionist, Emergency)
- ⬜ Break-glass access endpoint
- ⬜ Mobile app screens
- ⬜ Dashboard pages