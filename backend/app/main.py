from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.database import Base, engine
from app import models  # noqa: F401 - needed so tables register on Base before create_all

app = FastAPI(title="LuminAI API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # tighten this before deployment
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def on_startup():
    # For the hackathon build: create tables directly.
    # Once schema stabilizes, switch to Alembic migrations instead.
    Base.metadata.create_all(bind=engine)


@app.get("/health")
def health_check():
    return {"status": "ok"}


# Routers get added here as they're built, e.g.:
# from app.routers import auth, mothers, phm, records, agents
# app.include_router(auth.router, prefix="/auth", tags=["auth"])
# app.include_router(mothers.router, prefix="/mothers", tags=["mothers"])
# app.include_router(phm.router, prefix="/phm", tags=["phm"])
# app.include_router(records.router, prefix="/records", tags=["records"])
# app.include_router(agents.router, prefix="/agents", tags=["agents"])