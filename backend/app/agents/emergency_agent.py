"""
PLACEHOLDER. Kaveesha replaces this file with the real Emergency Agent
(read the instructions in the documentation kaveesha aiyeee :) ) - it's actually two separate
functions, since they're triggered by two different events:

- check_symptom_log(): triggered when a mother submits a symptom check-in.
- check_monitoring_trend(): triggered when a PHM logs a new monitoring entry.

The rest of the backend only depends on the function names and the keys in
their returned dicts - keep both exactly as they are below when building the
real versions, so nothing else needs to change.
"""


def check_symptom_log(symptoms: list[str]) -> dict:
    return {
        "danger_sign_detected": False,
        "risk_level": "none",
        "should_alert": False,
        "message_sinhala": "රෝග ලක්ෂණ තවම විශ්ලේෂණය කර නොමැත.",
    }


def check_monitoring_trend(recent_entries: list[dict]) -> dict:
    """
    recent_entries: last 3-4 ContinuousMonitoring rows for one mother,
    oldest first, as dicts (see docs/database_schema.md for field names).
    """
    return {
        "trend_detected": False,
        "risk_level": "none",
        "should_alert": False,
        "message_sinhala": "ප්‍රවණතා තවම විශ්ලේෂණය කර නොමැත.",
    }