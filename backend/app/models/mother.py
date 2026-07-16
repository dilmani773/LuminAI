import uuid
from datetime import datetime, date

from sqlalchemy import Column, String, DateTime, Date, Integer, ForeignKey, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.database import Base


class Mother(Base):
    """
    Pregnant mother - the primary user, digital equivalent of the Card A/B holder.

    Fields below split into two groups:
    - Profile fields: set once at registration, rarely change.
    - Static clinical fields: taken from Card A/B at registration, one-time
      background info (not the repeating visit data - that lives in ContinuousMonitoring).
    """
    __tablename__ = "mothers"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    # Profile
    full_name = Column(String, nullable=False)
    age = Column(Integer)
    phone = Column(String, unique=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    clinic_registration_date = Column(Date, default=date.today)

    # Static clinical info (from Card A/B, page 1-2)
    blood_group = Column(String)
    known_allergies = Column(String)          # comma separated, also used for break-glass access
    lmp_date = Column(Date)                    # Last Menstrual Period -> used to calc gestational week
    edd_date = Column(Date)                    # Estimated Date of Delivery
    gravidity = Column(String)                 # e.g. "G2 P1 C0"
    past_obstetric_history = Column(Text)      # summary of G1-G6 outcomes from Card A/B
    identified_risk_conditions = Column(Text)  # antenatal risk conditions & morbidities noted at registration

    phm_id = Column(UUID(as_uuid=True), ForeignKey("phms.id"), nullable=False)
    doctor_id = Column(UUID(as_uuid=True), ForeignKey("doctors.id"))  # assigned doctor, nullable until assigned

    created_at = Column(DateTime, default=datetime.utcnow)

    phm = relationship("PHM", back_populates="mothers")
    doctor = relationship("Doctor", back_populates="mothers")
    appointments = relationship("Appointment", back_populates="mother")
    reports = relationship("Report", back_populates="mother")
    monitoring_entries = relationship("ContinuousMonitoring", back_populates="mother")
    meal_plans = relationship("MealPlan", back_populates="mother")
    symptom_logs = relationship("SymptomLog", back_populates="mother")
    alerts = relationship("Alert", back_populates="mother")
    breakglass_accesses = relationship("BreakGlassAccess", back_populates="mother")

    def current_week(self) -> int | None:
        """Rough gestational week from LMP date - used to pick trimester-specific guidance."""
        if not self.lmp_date:
            return None
        return (date.today() - self.lmp_date).days // 7