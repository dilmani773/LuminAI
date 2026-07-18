from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from app.database import get_db
from app.models import PHM, Mother, Doctor
from app.schemas.phm import PHMRegisterRequest, PHMResponse
from app.schemas.mother import MotherRegisterRequest, MotherResponse
from app.schemas.doctor import DoctorRegisterRequest, DoctorResponse
from app.schemas.auth import LoginRequest, TokenResponse
from app.core.security import hash_password, verify_password, create_access_token

router = APIRouter()


@router.post("/register/phm", response_model=PHMResponse, status_code=status.HTTP_201_CREATED)
def register_phm(payload: PHMRegisterRequest, db: Session = Depends(get_db)):
    phm = PHM(
        full_name=payload.full_name,
        email=payload.email,
        hashed_password=hash_password(payload.password),
        moh_zone=payload.moh_zone,
        phone=payload.phone,
    )
    db.add(phm)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=400, detail="A PHM with this email already exists")
    db.refresh(phm)
    return phm


@router.post("/register/mother", response_model=MotherResponse, status_code=status.HTTP_201_CREATED)
def register_mother(payload: MotherRegisterRequest, db: Session = Depends(get_db)):
    # Confirm the PHM being registered under actually exists
    phm = db.query(PHM).filter(PHM.id == payload.phm_id).first()
    if not phm:
        raise HTTPException(status_code=404, detail="No PHM found with that phm_id")

    mother = Mother(
        full_name=payload.full_name,
        phone=payload.phone,
        hashed_password=hash_password(payload.password),
        phm_id=payload.phm_id,
        age=payload.age,
        blood_group=payload.blood_group,
        known_allergies=payload.known_allergies,
        lmp_date=payload.lmp_date,
        edd_date=payload.edd_date,
        gravidity=payload.gravidity,
        past_obstetric_history=payload.past_obstetric_history,
        identified_risk_conditions=payload.identified_risk_conditions,
    )
    db.add(mother)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=400, detail="A mother with this phone number already exists")
    db.refresh(mother)
    return mother


@router.post("/register/doctor", response_model=DoctorResponse, status_code=status.HTTP_201_CREATED)
def register_doctor(payload: DoctorRegisterRequest, db: Session = Depends(get_db)):
    doctor = Doctor(
        full_name=payload.full_name,
        email=payload.email,
        hashed_password=hash_password(payload.password),
        specialization=payload.specialization,
        phone=payload.phone,
    )
    db.add(doctor)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=400, detail="A doctor with this email already exists")
    db.refresh(doctor)
    return doctor


@router.post("/login", response_model=TokenResponse)
def login(payload: LoginRequest, db: Session = Depends(get_db)):
    """
    One login endpoint for all 3 roles. `identifier` is email for PHM/Doctor,
    phone for Mother. Checks each table in turn until a match is found.
    """
    phm = db.query(PHM).filter(PHM.email == payload.identifier).first()
    if phm and verify_password(payload.password, phm.hashed_password):
        token = create_access_token(str(phm.id), "phm")
        return TokenResponse(access_token=token, role="phm", user_id=str(phm.id))

    doctor = db.query(Doctor).filter(Doctor.email == payload.identifier).first()
    if doctor and verify_password(payload.password, doctor.hashed_password):
        token = create_access_token(str(doctor.id), "doctor")
        return TokenResponse(access_token=token, role="doctor", user_id=str(doctor.id))

    mother = db.query(Mother).filter(Mother.phone == payload.identifier).first()
    if mother and verify_password(payload.password, mother.hashed_password):
        token = create_access_token(str(mother.id), "mother")
        return TokenResponse(access_token=token, role="mother", user_id=str(mother.id))

    raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")