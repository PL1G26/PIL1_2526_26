# ============================================================
# IFRI_MentorLink — Authentication Router
# backend/routers/auth.py
# Endpoints: register, login, reset-password
# ============================================================

from datetime import timedelta
from typing import Any, Dict

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from sqlalchemy.orm import Session

from config import settings
from database import get_db
from models.user import User
from schemas.auth_schema import (
    LoginRequest,
    RegisterRequest,
    ResetPasswordRequest,
    TokenResponse,
)
from services.auth_service import (
    create_access_token,
    decode_access_token,
    hash_password,
    verify_password,
)

# ──── ROUTER CONFIGURATION ───────────────────────────────────
router = APIRouter()

# OAuth2 scheme for extracting token from Authorization header
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")

# ──── DEPENDENCIES ───────────────────────────────────────────
async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
) -> User:
    """
    Dépendance FastAPI pour récupérer l'utilisateur connecté
    à partir du token JWT.
    
    Usage:
    @router.get("/protected")
    def protected_route(current_user: User = Depends(get_current_user)):
        ...
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        payload = decode_access_token(token)
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    
    user = db.query(User).filter(User.id == int(user_id)).first()
    if user is None:
        raise credentials_exception
    
    return user


async def get_current_user_optional(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
) -> User | None:
    """
    Version optionnelle de get_current_user.
    Retourne None si pas de token ou token invalide.
    """
    try:
        return await get_current_user(token, db)
    except HTTPException:
        return None


# ──── AUTHENTICATION ENDPOINTS ───────────────────────────────
@router.post(
    "/register",
    response_model=TokenResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Inscription d'un nouvel utilisateur",
)
async def register(
    user_data: RegisterRequest,
    db: Session = Depends(get_db),
) -> TokenResponse:
    """
    Inscription d'un nouvel utilisateur sur la plateforme.
    
    Vérifie que l'email et le numéro de téléphone ne sont pas déjà utilisés,
    puis crée le compte avec le mot de passe haché.
    """
    # Vérifier si l'email existe déjà
    existing_email = db.query(User).filter(User.email == user_data.email).first()
    if existing_email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cet email est déjà utilisé",
        )
    
    # Vérifier si le numéro de téléphone existe déjà
    existing_phone = db.query(User).filter(
        User.phone_number == user_data.phone_number
    ).first()
    if existing_phone:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Ce numéro de téléphone est déjà utilisé",
        )
    
    # Hasher le mot de passe
    hashed_password = hash_password(user_data.password)
    
    # Créer l'utilisateur
    new_user = User(
        first_name=user_data.first_name,
        last_name=user_data.last_name,
        email=user_data.email,
        phone_number=user_data.phone_number,
        password_hash=hashed_password,
        field_of_study=user_data.field_of_study,
        level=user_data.level,
        bio=user_data.bio,
    )
    
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    # Générer le token JWT
    access_token = create_access_token(
        data={"sub": str(new_user.id)},
        expires_delta=timedelta(hours=settings.token_expire_hours),
    )
    
    return TokenResponse(
        access_token=access_token,
        token_type="bearer",
        user={
            "id": new_user.id,
            "first_name": new_user.first_name,
            "last_name": new_user.last_name,
            "email": new_user.email,
            "field_of_study": new_user.field_of_study,
            "level": new_user.level,
        },
    )


@router.post(
    "/login",
    response_model=TokenResponse,
    summary="Connexion utilisateur",
)
async def login(
    credentials: LoginRequest,
    db: Session = Depends(get_db),
) -> TokenResponse:
    """
    Connexion utilisateur avec email et mot de passe.
    
    Vérifie les identifiants et retourne un token JWT
    si les informations sont correctes.
    """
    # Rechercher l'utilisateur par email
    user = db.query(User).filter(User.email == credentials.email).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email ou mot de passe incorrect",
        )
    
    # Vérifier le mot de passe
    if not verify_password(credentials.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email ou mot de passe incorrect",
        )
    
    # Générer le token JWT
    access_token = create_access_token(
        data={"sub": str(user.id)},
        expires_delta=timedelta(hours=settings.token_expire_hours),
    )
    
    return TokenResponse(
        access_token=access_token,
        token_type="bearer",
        user={
            "id": user.id,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "email": user.email,
            "field_of_study": user.field_of_study,
            "level": user.level,
        },
    )


@router.post(
    "/reset-password",
    status_code=status.HTTP_200_OK,
    summary="Réinitialisation du mot de passe",
)
async def reset_password(
    request: ResetPasswordRequest,
    db: Session = Depends(get_db),
) -> Dict[str, str]:
    """
    Demande de réinitialisation du mot de passe.
    
    NOTE: Implémentation basique - en production,
    il faudrait envoyer un email avec un lien de reset.
    """
    user = db.query(User).filter(User.email == request.email).first()
    
    if not user:
        # Ne pas révéler si l'email existe ou non
        return {"message": "Si l'email existe, un lien de réinitialisation a été envoyé"}
    
    # TODO: Implémenter l'envoi d'email avec token de reset
    # Pour l'instant, retourne juste un message générique
    
    return {"message": "Si l'email existe, un lien de réinitialisation a été envoyé"}


@router.get(
    "/me",
    summary="Récupérer le profil de l'utilisateur connecté",
)
async def get_me(
    current_user: User = Depends(get_current_user),
) -> Dict[str, Any]:
    """
    Retourne les informations de l'utilisateur connecté.
    Requiert un token JWT valide.
    """
    return {
        "id": current_user.id,
        "first_name": current_user.first_name,
        "last_name": current_user.last_name,
        "email": current_user.email,
        "phone_number": current_user.phone_number,
        "profile_photo": current_user.profile_photo,
        "field_of_study": current_user.field_of_study,
        "level": current_user.level,
        "bio": current_user.bio,
        "created_at": current_user.created_at.isoformat() if current_user.created_at else None,
        "updated_at": current_user.updated_at.isoformat() if current_user.updated_at else None,
    }