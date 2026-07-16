import uuid
from datetime import datetime

from sqlalchemy import Column, String, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.database import Base


class Doctor(Base):
    """
    Doctor - a real login role. One doctor is assigned to many mothers (1:M),
    but is not restricted to only those mothers: any doctor can use break-glass
    access to view a mother's critical profile in an emergency, regardless of
    assignment. See BreakGlassAccess for that logged access path.
    """
    __tablename__ = "doctors"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    full_name = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    specialization = Column(String)  # e.g. "Obstetrician"
    phone = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)

    mothers = relationship("Mother", back_populates="doctor")
    breakglass_accesses = relationship("BreakGlassAccess", back_populates="doctor")