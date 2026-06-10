"""
Schémas Pydantic pour l'authentification.
"""
from pydantic import BaseModel, EmailStr, Field
from typing import Optional


class RegisterRequest(BaseModel):
    """Schéma pour l'inscription d'un nouvel utilisateur."""
    first_name: str = Field(..., min_length=1, max_length=50)
    last_name: str = Field(..., min_length=1, max_length=50)
    email: EmailStr
    phone_number: str = Field(..., min_length=1, max_length=20)
    password: str = Field(..., min_length=6)
    field_of_study: str = Field(..., pattern="^(IA|IM|GL|SE&IoT|SI)$")
    level: str = Field(..., pattern="^(L1|L2|L3|M1|M2)$")
    bio: Optional[str] = None


class LoginRequest(BaseModel):
    """Schéma pour la connexion utilisateur."""
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    """Schéma de réponse après connexion."""
    access_token: str
    token_type: str = "bearer"
    user: dict  # User info


class ResetPasswordRequest(BaseModel):
    """Schéma pour la réinitialisation du mot de passe."""
    email: EmailStr