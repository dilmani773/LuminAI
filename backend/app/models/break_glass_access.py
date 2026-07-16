import uuid
from datetime import datetime

from sqlalchemy import Column, String, DateTime, ForeignKey, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.database import Base


class BreakGlassAccess(Base):
    """
    Logged emergency access: a doctor who is NOT the mother's assigned doctor
    looks up her critical profile (blood type, allergies, recent reports,
    risk level) in an urgent situation. Every access is recorded with a
    reason for accountability - this is what makes "any doctor can view any
    mother in an emergency" safe rather than an open data-privacy hole.
    """
    __tablename__ = "breakglass_accesses"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    mother_id = Column(UUID(as_uuid=True), ForeignKey("mothers.id"), nullable=False)
    doctor_id = Column(UUID(as_uuid=True), ForeignKey("doctors.id"), nullable=False)

    reason = Column(Text, nullable=False)  # short text, e.g. "referred for high BP at Base Hospital"
    accessed_at = Column(DateTime, default=datetime.utcnow)

    mother = relationship("Mother", back_populates="breakglass_accesses")
    doctor = relationship("Doctor", back_populates="breakglass_accesses")