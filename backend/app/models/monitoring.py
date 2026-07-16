import uuid
from datetime import datetime

from sqlalchemy import Column, String, DateTime, Float, Boolean, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.database import Base


class ContinuousMonitoring(Base):
    """
    One row per PHM visit - the recurring measurements from Card A's
    'Clinic Care' table (BP, urine, oedema, fundal height, FHS, weight etc).
    This is the time-series data the Emergency Agent scans for dangerous
    trends, and the Nutritionist Agent uses alongside Reports to shape
    meal plans.
    """
    __tablename__ = "continuous_monitoring"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    mother_id = Column(UUID(as_uuid=True), ForeignKey("mothers.id"), nullable=False)
    recorded_by_phm_id = Column(UUID(as_uuid=True), ForeignKey("phms.id"), nullable=False)

    visit_date = Column(DateTime, nullable=False, default=datetime.utcnow)

    bp_systolic = Column(Float)
    bp_diastolic = Column(Float)
    weight_kg = Column(Float)
    fundal_height_cm = Column(Float)
    urine_protein = Column(String)   # "negative" | "trace" | "+1" | "+2" | "+3"
    oedema = Column(Boolean, default=False)
    fhs = Column(String)             # fetal heart sound, e.g. "present, 140bpm"

    created_at = Column(DateTime, default=datetime.utcnow)

    mother = relationship("Mother", back_populates="monitoring_entries")
    alerts = relationship("Alert", back_populates="monitoring_entry")