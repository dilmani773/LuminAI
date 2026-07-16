# LuminAI — Project Status

Team Pulse 404 · HackElite 3.0

## Team

| Name | Role | GitHub |
|---|---|---|
| Kaveesha Madhushan | Team Lead & ML/AI Developer | Kaveesha-Madhushan17 |
| Hiyumi Dilmani Suriyapperuma | AI & Backend Developer | dilmani773 |
| Fathima Akeela | Mobile App Developer | acfakeela |
| Hareen Liyanage | DevOps & Frontend Developer | Hareen-Liyanage |

## Full file structure

```
luminai/
├── backend/                                # FastAPI - Inaaya
│   ├── app/
│   │   ├── main.py                         # ✅ done
│   │   ├── config.py                       # ✅ done
│   │   ├── database.py                     # ✅ done
│   │   ├── __init__.py                     # ✅ done
│   │   │
│   │   ├── models/                         # ✅ done - all 10 tables
│   │   │   ├── __init__.py
│   │   │   ├── phm.py
│   │   │   ├── doctor.py
│   │   │   ├── mother.py
│   │   │   ├── appointment.py
│   │   │   ├── report.py
│   │   │   ├── monitoring.py
│   │   │   ├── meal_plan.py
│   │   │   ├── symptom_log.py
│   │   │   ├── alert.py
│   │   │   └── break_glass_access.py
│   │   │
│   │   ├── schemas/                        # ⬜ not started
│   │   │   ├── phm.py
│   │   │   ├── mother.py
│   │   │   ├── doctor.py
│   │   │   ├── appointment.py
│   │   │   ├── report.py
│   │   │   ├── monitoring.py
│   │   │   ├── meal_plan.py
│   │   │   ├── symptom_log.py
│   │   │   ├── alert.py
│   │   │   └── agent_output.py             # strict schemas every LLM response must match
│   │   │
│   │   ├── routers/                        # ⬜ not started - next up
│   │   │   ├── auth.py                     # 🔜 building next
│   │   │   ├── phm.py
│   │   │   ├── mothers.py
│   │   │   ├── doctors.py
│   │   │   ├── appointments.py
│   │   │   ├── reports.py
│   │   │   ├── monitoring.py
│   │   │   ├── meal_plans.py
│   │   │   ├── symptom_logs.py
│   │   │   ├── alerts.py
│   │   │   └── break_glass.py
│   │   │
│   │   ├── agents/                         # ⬜ not started
│   │   │   ├── orchestrator.py
│   │   │   ├── report_analysis_agent.py
│   │   │   ├── nutritionist_agent.py
│   │   │   ├── emergency_agent.py
│   │   │   └── prompts/
│   │   │       ├── report_analysis_prompt.py
│   │   │       ├── nutritionist_prompt.py
│   │   │       └── emergency_prompt.py
│   │   │
│   │   ├── services/                       # ⬜ not started
│   │   │   ├── ocr_service.py
│   │   │   ├── rag_service.py
│   │   │   ├── trend_service.py
│   │   │   └── notification_service.py
│   │   │
│   │   ├── core/                           # ⬜ not started
│   │   │   ├── security.py                 # JWT auth, role-based access
│   │   │   └── guardrails.py               # output validation
│   │   │
│   │   └── utils/
│   │
│   ├── alembic/                            # ⬜ not started (using create_all for now)
│   ├── tests/                              # ⬜ not started
│   ├── requirements.txt                    # ✅ done
│   ├── .env.example                        # ✅ done
│   └── Dockerfile                          # ✅ done
│
├── mobile_app/                             # Flutter - Fathima
│   ├── lib/
│   │   ├── main.dart                       # ⬜ not started
│   │   ├── screens/
│   │   │   ├── auth/
│   │   │   ├── upload_report/
│   │   │   ├── symptom_checkin/
│   │   │   ├── meal_plan_view/
│   │   │   └── my_records/
│   │   ├── widgets/
│   │   ├── services/api_service.dart
│   │   ├── models/
│   │   └── l10n/
│   └── pubspec.yaml
│
├── dashboard/                              # React+TS - Hareen
│   ├── src/
│   │   ├── App.tsx                         # ⬜ not started
│   │   ├── pages/
│   │   │   ├── PatientList/
│   │   │   ├── PatientDetail/
│   │   │   ├── Appointments/
│   │   │   ├── MealPlanReview/
│   │   │   ├── Alerts/
│   │   │   └── DoctorBreakGlass/
│   │   ├── components/
│   │   ├── services/api.ts
│   │   ├── hooks/
│   │   └── types/
│   └── package.json
│
├── data/                                   # ⬜ not started
│   ├── sri_lankan_foods.json
│   └── moh_guidelines/
│
├── infra/
│   └── docker-compose.yml                  # ✅ done
│
├── docs/                                   # ✅ done
│   ├── database_schema.md / .docx
│   └── api_contract.md / .docx
│
└── README.md                               # ✅ done
```

## What's been done so far

- Finalized the database schema across 3 rounds of ERD revisions (roles, reports,
  continuous monitoring, dual-trigger alerts, break-glass access).
- Built and tested all 10 SQLAlchemy models — tables create cleanly, all
  relationships resolve.
- FastAPI app skeleton with CORS, health check, and auto table creation on startup.
- Docker Compose setup (Postgres + backend) — confirmed working end-to-end on
  Inaaya's machine.
- `docs/database_schema.md` — every field, type, and enum value documented for
  the whole team, plus what each of the 3 agents reads/writes.
- `docs/api_contract.md` — full planned endpoint list so mobile/dashboard can
  build against the contract before every route is implemented.
- `README.md` — setup instructions + troubleshooting for Docker/Windows issues
  already hit and solved.
- Code pushed to GitHub — team can now clone and run locally.

## What's next (in order)

1. **Auth** — register/login for PHM, Mother, Doctor, returns JWT. Unblocks
   everyone else's login screens.
2. **Mothers + PHM CRUD routers** — profile view/edit, PHM's mother list.
3. **Appointments router** — simple CRUD, no AI.
4. **Reports upload + Report Analysis Agent** — first real AI piece (OCR +
   extraction + Sinhala explanation).
5. **Continuous Monitoring router + trend detection logic.**
6. **Nutritionist Agent + Emergency Agent.**
7. **Break-glass access endpoint.**

Mobile app and dashboard work can start in parallel once auth + schemas exist,
using `docs/api_contract.md` as the reference.