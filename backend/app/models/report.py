import uuid
from datetime import datetime

from sqlalchemy import Column, String, DateTime, ForeignKey, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.database import Base


class Report(Base):
    """
    Any report uploaded for a mother: FBC, urine test, blood sugar, ultrasound,
    scanned Card A/B pages, etc. Uploaded by the mother herself or by her PHM
    on her behalf. Analyzed by the Report Analysis Agent, which fills in
    risk_level and explanation_sinhala after processing.
    """
    __tablename__ = "reports"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    mother_id = Column(UUID(as_uuid=True), ForeignKey("mothers.id"), nullable=False)

    report_type = Column(String, nullable=False)  # "fbc" | "urine" | "blood_sugar" | "ultrasound" | "card_scan" | "other"
    file_url = Column(String, nullable=False)

    uploaded_by_role = Column(String, nullable=False)  # "mother" | "phm"
    uploaded_by_id = Column(UUID(as_uuid=True), nullable=False)  # mother_id or phm_id depending on role

    # Filled in by the Report Analysis Agent after processing
    hb_level = Column(String)
    blood_sugar = Column(String)
    urine_protein = Column(String)
    risk_level = Column(String)  # "low" | "moderate" | "high"
    explanation_sinhala = Column(Text)

    created_at = Column(DateTime, default=datetime.utcnow)

    mother = relationship("Mother", back_populates="reports")
    meal_plans = relationship("MealPlan", back_populates="source_report")