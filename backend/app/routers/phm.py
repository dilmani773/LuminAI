from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import PHM, Mother
from app.schemas.phm import PHMResponse
from app.schemas.mother import MotherResponse
from app.core.security import require_role, CurrentUser

router = APIRouter()


@router.get("/me", response_model=PHMResponse)
def get_my_profile(db: Session = Depends(get_db), user: CurrentUser = Depends(require_role("phm"))):
    phm = db.query(PHM).filter(PHM.id == UUID(user.id)).first()
    if not phm:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="PHM not found")
    return phm


@router.get("/mothers", response_model=list[MotherResponse])
def get_my_mothers(db: Session = Depends(get_db), user: CurrentUser = Depends(require_role("phm"))):
    """List every mother managed by the currently logged-in PHM."""
    return db.query(Mother).filter(Mother.phm_id == UUID(user.id)).all()