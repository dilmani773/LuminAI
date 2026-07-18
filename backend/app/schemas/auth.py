from pydantic import BaseModel


class LoginRequest(BaseModel):
    """
    Same login endpoint serves all 3 roles - identifier is email (PHM/Doctor)
    or phone (Mother). Backend checks all 3 tables to find a match.
    """
    identifier: str  # email or phone
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    role: str
    user_id: str