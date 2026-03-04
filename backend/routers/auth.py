from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, EmailStr
import secrets

from config import settings

router = APIRouter(prefix="/auth", tags=["auth"])


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class LoginResponse(BaseModel):
    access_token: str
    token_type: str
    message: str


@router.post("/login", response_model=LoginResponse)
def login(payload: LoginRequest):
    email_ok = secrets.compare_digest(payload.email.lower(), settings.ADMIN_EMAIL.lower())
    password_ok = secrets.compare_digest(payload.password, settings.ADMIN_PASSWORD)

    if not (email_ok and password_ok):
        raise HTTPException(status_code=401, detail="Credenciales invalidas")

    return LoginResponse(
        access_token="demo-token",
        token_type="bearer",
        message="Login exitoso",
    )
