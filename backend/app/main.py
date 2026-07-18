from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.database import Base, engine
from app import models  # noqa: F401 - needed so tables register on Base before create_all
from app.routers import auth, mothers, phm, appointments, reports, monitoring, symptom_logs, doctors, break_glass

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


app.include_router(auth.router, prefix="/auth", tags=["auth"])
app.include_router(mothers.router, prefix="/mothers", tags=["mothers"])
app.include_router(phm.router, prefix="/phm", tags=["phm"])
app.include_router(appointments.router, prefix="/appointments", tags=["appointments"])
app.include_router(reports.router, prefix="/reports", tags=["reports"])
app.include_router(monitoring.router, prefix="/monitoring", tags=["monitoring"])
app.include_router(symptom_logs.router, prefix="/symptom-logs", tags=["symptom-logs"])
app.include_router(doctors.router, prefix="/doctors", tags=["doctors"])
app.include_router(break_glass.router, prefix="/break-glass", tags=["break-glass"])

# More routers get added here as they're built, e.g.:
# from app.routers import meal_plans, alerts
# app.include_router(meal_plans.router, prefix="/meal-plans", tags=["meal-plans"])