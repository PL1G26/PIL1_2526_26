# ============================================================
# IFRI_MentorLink — Configuration FastAPI
# backend/config.py
# Charge les variables d'environnement
# ============================================================

from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field
from typing import List
import os
from dotenv import load_dotenv

# Charger les variables depuis .env
load_dotenv()

# Helper function to parse comma-separated list from env
def get_allowed_origins() -> List[str]:
    """Parse ALLOWED_ORIGINS from env or return default"""
    env_origins = os.getenv("ALLOWED_ORIGINS", "")
    if env_origins:
        return [origin.strip() for origin in env_origins.split(",")]
    return [
        "http://localhost:5173",
        "http://localhost:3000",
        "http://127.0.0.1:5173",
        "http://127.0.0.1:3000",
    ]


class Settings(BaseSettings):
    """Configuration globale de l'application FastAPI"""
    
    # Pydantic v2 configuration
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="allow"
    )

    # ── DATABASE ─────────────────────────────────────────────
    database_url: str = Field(
        default="postgresql://postgres:password@localhost:5432/ifri_mentorlink"
    )

    # Supabase (optionnel)
    supabase_url: str = Field(default="")
    supabase_anon_key: str = Field(default="")
    supabase_service_key: str = Field(default="")

    # ── JWT AUTHENTICATION ───────────────────────────────────
    secret_key: str = Field(
        default="change-this-secret-key-in-production"
    )
    token_expire_hours: int = Field(default=24)
    algorithm: str = Field(default="HS256")

    # ── CORS & API ───────────────────────────────────────────
    # Use a private field to avoid Pydantic trying to parse from env
    allowed_origins: List[str] = Field(default_factory=get_allowed_origins)

    # ── SERVER ───────────────────────────────────────────────
    host: str = Field(default="0.0.0.0")
    port: int = Field(default=8000)
    env: str = Field(default="development")

    # ── LOGGING ──────────────────────────────────────────────
    log_level: str = Field(default="INFO")

    # ── EMAIL (optionnel) ────────────────────────────────────
    smtp_server: str = Field(default="")
    smtp_port: int = Field(default=587)
    smtp_user: str = Field(default="")
    smtp_password: str = Field(default="")
    sender_email: str = Field(default="noreply@ifri-mentorlink.com")

    # ── AWS S3 (optionnel, pour photos de profil) ───────────
    aws_access_key_id: str = Field(default="")
    aws_secret_access_key: str = Field(default="")
    aws_region: str = Field(default="us-east-1")
    s3_bucket_name: str = Field(default="")

    # ── REDIS (optionnel, pour cache) ────────────────────────
    redis_url: str = Field(default="")

    def is_production(self) -> bool:
        """Vérifie si on est en production"""
        return self.env == "production"

    def is_development(self) -> bool:
        """Vérifie si on est en développement"""
        return self.env == "development"


# Créer une instance globale des paramètres
settings = Settings()

# ============================================================
# USAGE DANS VOTRE CODE:
# ============================================================
# from backend.config import settings
# 
# # Utiliser les paramètres
# print(settings.database_url)
# print(settings.secret_key)
# 
# # Créer la connexion à la BDD
# engine = create_engine(settings.database_url)
# 
# # Configurer CORS
# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=settings.allowed_origins,
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )
# ============================================================
