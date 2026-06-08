from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import logging
from datetime import datetime

from config import settings
from database import test_connection

# ──── LOGGING SETUP ──────────────────────────────────────────
logging.basicConfig(
    level=settings.log_level,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# ──── FASTAPI INITIALIZATION ─────────────────────────────────
app = FastAPI(
    title="IFRI_MentorLink API",
    description="API REST pour la plateforme de mentorat académique IFRI",
    version="1.0.0",
    docs_url="/docs" if settings.is_development() else None,  # Swagger UI
    redoc_url="/redoc" if settings.is_development() else None,  # ReDoc
)

# ──── CORS MIDDLEWARE ────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ──── HEALTH CHECK ENDPOINT ──────────────────────────────────
@app.get("/health")
async def health_check():
    """Endpoint de vérification que l'API est en ligne"""
    return {
        "status": "ok",
        "timestamp": datetime.utcnow().isoformat(),
        "environment": settings.env,
    }

# ──── ROOT ENDPOINT ──────────────────────────────────────────
@app.get("/")
async def root():
    """Endpoint racine"""
    return {
        "message": "Bienvenue sur IFRI_MentorLink API",
        "version": "1.0.0",
        "docs": "/docs",
        "environment": settings.env,
    }

# ──── ROUTER IMPORTS ──────────────────────────────────────────
from routers import auth, chat, users, skills, posts, matches

app.include_router(auth.router, prefix="/api/auth", tags=["Authentication"])
app.include_router(users.router, prefix="/api/users", tags=["Users"])
app.include_router(skills.router, prefix="/api/skills", tags=["Skills"])
app.include_router(posts.router, prefix="/api/posts", tags=["Mentorship Posts"])
app.include_router(matches.router, prefix="/api/matches", tags=["Matching"])
app.include_router(chat.router, prefix="/api", tags=["Chat"])

# ──── EXCEPTION HANDLING ─────────────────────────────────────
@app.exception_handler(Exception)
async def global_exception_handler(request, exc : Exception):
    """Gestionnaire global des exceptions"""
    logger.error(f"Exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"},
    )

# ──── STARTUP & SHUTDOWN EVENTS ──────────────────────────────
@app.on_event("startup")
async def startup_event():
    """Événement au démarrage"""
    logger.info("🚀 IFRI_MentorLink API démarrée")
    logger.info(f"Environment: {settings.env}")
    logger.info(f"Database: {settings.database_url.split('@')[1] if '@' in settings.database_url else 'N/A'}")
    logger.info(f"Allowed origins: {settings.allowed_origins}")
    
    # Test database connection
    if test_connection():
        logger.info("✓ Database connection successful!")
    else:
        logger.warning("⚠️  Database connection failed - check your DATABASE_URL")

@app.on_event("shutdown")
async def shutdown_event():
    """Événement à l'arrêt"""
    logger.info("🛑 IFRI_MentorLink API arrêtée")

# ============================================================
# DÉMARRAGE LOCAL:
# ============================================================
# uvicorn backend.main:app --reload
# 
# ou avec un port personnalisé:
# uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload
#
# Swagger UI disponible à: http://localhost:8000/docs
# ReDoc disponible à: http://localhost:8000/redoc
# ============================================================

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "backend.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.is_development(),
    )
