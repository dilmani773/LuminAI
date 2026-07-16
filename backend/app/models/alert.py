import uuid
from datetime import datetime

from sqlalchemy import Column, String, DateTime, ForeignKey, Boolean
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.database import Base


class Alert(Base):
    """
    An alert raised to the responsible PHM by the Emergency Agent.

    Created from one of two triggers:
    - source_type = "symptom_log": mother self-reported a danger sign.
    - source_type = "monitoring_trend": PHM logged a new ContinuousMonitoring
      entry and the agent detected a dangerous trend across recent visits
      (e.g. BP climbing, fundal height stalling), even if the latest single
      reading looked fine on its own.

    Exactly one of symptom_log_id / monitoring_entry_id is set, matching source_type.
    """
    __tablename__ = "alerts"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    mother_id = Column(UUID(as_uuid=True), ForeignKey("mothers.id"), nullable=False)
    phm_id = Column(UUID(as_uuid=True), ForeignKey("phms.id"), nullable=False)

    source_type = Column(String, nullable=False)  # "symptom_log" | "monitoring_trend"
    symptom_log_id = Column(UUID(as_uuid=True), ForeignKey("symptom_logs.id"))
    monitoring_entry_id = Column(UUID(as_uuid=True), ForeignKey("continuous_monitoring.id"))

    severity = Column(String, nullable=False)  # "high" | "critical"
    message_sinhala = Column(String, nullable=False)
    status = Column(String, default="open")     # "open" | "resolved"
    is_resolved = Column(Boolean, default=False)

    created_at = Column(DateTime, default=datetime.utcnow)
    resolved_at = Column(DateTime)

    mother = relationship("Mother", back_populates="alerts")
    phm = relationship("PHM", back_populates="alerts")
    symptom_log = relationship("SymptomLog", back_populates="alert")
    monitoring_entry = relationship("ContinuousMonitoring", back_populates="alerts")