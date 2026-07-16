import uuid
from datetime import datetime

from sqlalchemy import Column, String, DateTime, ForeignKey, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.database import Base


class Appointment(Base):
    """A clinic visit scheduled by the PHM for a mother she manages."""
    __tablename__ = "appointments"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    mother_id = Column(UUID(as_uuid=True), ForeignKey("mothers.id"), nullable=False)
    phm_id = Column(UUID(as_uuid=True), ForeignKey("phms.id"), nullable=False)

    scheduled_date = Column(DateTime, nullable=False)
    status = Column(String, default="scheduled")  # "scheduled" | "completed" | "missed" | "cancelled"
    notes = Column(Text)

    created_at = Column(DateTime, default=datetime.utcnow)

    mother = relationship("Mother", back_populates="appointments")
    phm = relationship("PHM", back_populates="appointments")