from datetime import datetime, timedelta
from typing import Literal

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from passlib.context import CryptContext
from pydantic import BaseModel

from app.config import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

Role = Literal["phm", "mother", "doctor"]


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(subject_id: str, role: Role) -> str:
    """Encodes a JWT carrying the user's id and role - role is what routers
    use to decide what a token is allowed to touch (e.g. only a doctor can
    hit /break-glass, only a phm can resolve alerts)."""
    expire = datetime.utcnow() + timedelta(minutes=settings.access_token_expire_minutes)
    payload = {"sub": subject_id, "role": role, "exp": expire}
    return jwt.encode(payload, settings.secret_key, algorithm=settings.algorithm)


class CurrentUser(BaseModel):
    id: str
    role: Role


def get_current_user(token: str = Depends(oauth2_scheme)) -> CurrentUser:
    """Decodes the bearer token on every protected request. Raises 401 if the
    token is missing, expired, or tampered with."""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
        user_id = payload.get("sub")
        role = payload.get("role")
        if user_id is None or role is None:
            raise credentials_exception
        return CurrentUser(id=user_id, role=role)
    except JWTError:
        raise credentials_exception


def require_role(*allowed_roles: Role):
    """
    Dependency factory for routes restricted to specific roles, e.g.:
        @router.post("/break-glass/{mother_id}")
        def access(..., user: CurrentUser = Depends(require_role("doctor"))):
    """
    def checker(user: CurrentUser = Depends(get_current_user)) -> CurrentUser:
        if user.role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"This action requires one of these roles: {', '.join(allowed_roles)}",
            )
        return user
    return checker