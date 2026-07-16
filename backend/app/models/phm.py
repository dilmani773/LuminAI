import uuid
from datetime import datetime

from sqlalchemy import Column, String, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.database import Base


class PHM(Base):
    """Public Health Midwife - manages a caseload of mothers."""
    __tablename__ = "phms"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    full_name = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    moh_zone = Column(String, nullable=False)  # which MOH area/division they cover
    phone = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)

    mothers = relationship("Mother", back_populates="phm")
    appointments = relationship("Appointment", back_populates="phm")
    alerts = relationship("Alert", back_populates="phm")