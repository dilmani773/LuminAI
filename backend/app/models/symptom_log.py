import uuid
from datetime import datetime

from sqlalchemy import Column, String, DateTime, ForeignKey, Boolean
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.database import Base


class SymptomLog(Base):
    """A self-reported symptom check-in, used when the mother is not near her PHM."""
    __tablename__ = "symptom_logs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    mother_id = Column(UUID(as_uuid=True), ForeignKey("mothers.id"), nullable=False)

    symptoms = Column(String, nullable=False)  # comma-separated symptom codes reported
    danger_sign_detected = Column(Boolean, default=False)
    risk_level = Column(String)  # "none" | "low" | "high" | "critical"

    created_at = Column(DateTime, default=datetime.utcnow)

    mother = relationship("Mother", back_populates="symptom_logs")
    alert = relationship("Alert", back_populates="symptom_log", uselist=False)