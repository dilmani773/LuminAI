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
└── docs/          # database_schema, api_contract, per-teammate instructions - READ THESE before building
```

Read `docs/database_schema.md` and `docs/api_contract.md` first — they define
every field name and endpoint your part will talk to. The backend is fully
built, so both docs describe the real, working API, not a plan. If something
there doesn't match what you actually see, that's a bug — raise it in the
group chat rather than guessing around it.

Also check `docs/instructions_<your-name>_<your-part>.md` — written
specifically for your piece (agents / dashboard / mobile app), with concrete
build order and gotchas.

## Running the backend locally (everyone needs this working)

**Prerequisite: Docker Desktop must be installed AND running.**
Download: https://www.docker.com/products/docker-desktop/
After installing, open the Docker Desktop app itself and wait until it shows
"running" (whale icon steady in system tray / menu bar). `docker --version`
only checks the CLI is installed — it does NOT mean the engine is running.

```bash
git clone <repo-url>
cd LuminAI
```

**Set up your `.env` file** — this is not in git on purpose (it holds secret
API keys), so everyone creates their own local copy:
```bash
cd backend
cp .env.example .env
```
Then ask Inaaya for the real `GEMINI_API_KEY` / `ANTHROPIC_API_KEY` values
and paste them into your `.env`. Get these privately (not pasted in the
group chat), and never commit `.env` itself.

**Run it:**
```bash
cd ../infra
docker compose up --build
```

Wait for both `postgres-1` and `backend-1` logs to appear, ending with
`Application startup complete`. Then open:

```
http://localhost:8000/docs
```

You should see the full FastAPI docs page listing every router: auth, phm,
mothers, doctors, appointments, reports, monitoring, symptom-logs,
meal-plans, alerts, break-glass. That means Postgres + backend are both
running and talking to each other correctly.

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

**"Statements must be separated by newlines" / other syntax errors on lines that look fine**
Almost always curly/smart quotes (`"` `"`) instead of straight quotes (`"`)
sneaking in from copy-pasting through Word, Google Docs, or certain
keyboards. Delete the line and retype it directly in your code editor rather
than pasting, especially for lines containing Sinhala text in quotes.

**Made a code change and don't see it reflected?**
The Docker setup uses `--reload`, so changes to backend code auto-reload. If
you added a brand new file/folder or changed `requirements.txt`, stop
(`Ctrl+C`) and rerun `docker compose up --build` to pick it up properly.

**401 Unauthorized when testing an endpoint in `/docs`**
You need to authorize first: call `POST /auth/login`, copy the
`access_token` from the response, click the green "Authorize" button at the
top of the `/docs` page, paste the token in (no need to type "Bearer"), then
retry your request.

## Status

- ✅ Database models (10 tables)
- ✅ Docker + Postgres setup
- ✅ Full documentation (schema, API contract, per-teammate instructions)
- ✅ Auth (register/login for PHM, Mother, Doctor)
- ✅ All CRUD routers — mothers, phm, doctors, appointments, reports, monitoring, symptom-logs, meal-plans, alerts, break-glass
- ✅ Placeholder AI agents wired in and tested end-to-end (safe "not yet analyzed" responses, but the full save/alert pipeline around them is proven to work)
- 🔜 Real AI agent logic — Report Analysis, Nutritionist, Emergency (Kaveesha)
- ⬜ Mobile app screens (Akeela)
- ⬜ Dashboard pages (Hareen)

**Backend is done.** Everything left is: Kaveesha replacing the 3 placeholder
agent files with real logic, and Hareen/Akeela building their UIs against
the now-finalized `docs/api_contract.md`.