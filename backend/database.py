# ============================================================
# IFRI_MentorLink — Database Configuration
# backend/database.py
# Configuration SQLAlchemy pour Supabase/PostgreSQL
# ============================================================

from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import NullPool
import logging
from sqlalchemy import text

from config import settings

logger = logging.getLogger(__name__)

# ──── ENGINE CONFIGURATION ───────────────────────────────────
# Use NullPool pour éviter les problèmes de connexion en dev
# En production, utiliser QueuePool (défaut)

# Build engine kwargs based on environment
engine_kwargs = {
    "echo": settings.is_development(),  # Afficher les requêtes SQL en dev
    "pool_pre_ping": True,  # Vérifie la connexion avant utilisation
    "pool_recycle": 3600,  # Recycle les connexions après 1h
}

# Add pool configuration only if not using NullPool
if settings.is_development():
    engine_kwargs["poolclass"] = NullPool
else:
    engine_kwargs["pool_size"] = 5
    engine_kwargs["max_overflow"] = 10

engine = create_engine(settings.database_url, **engine_kwargs)

# ──── SESSION FACTORY ────────────────────────────────────────
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)

# ──── BASE CLASS POUR LES MODÈLES ───────────────────────────
Base = declarative_base()

# ──── DEPENDENCY INJECTION (pour FastAPI) ───────────────────
def get_db() -> Session:
    """
    Dépendance FastAPI pour obtenir une session de base de données.
    
    Usage dans une route:
    @app.get("/users/me")
    def get_current_user(db: Session = Depends(get_db)):
        ...
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# ──── INITIALIZATION FUNCTIONS ───────────────────────────────
def create_all_tables():
    """
    Crée toutes les tables basées sur les modèles SQLAlchemy.
    À utiliser UNIQUEMENT en développement ou migration.
    
    Usage:
    from backend.database import create_all_tables
    create_all_tables()
    """
    logger.info("Creating database tables...")
    Base.metadata.create_all(bind=engine)
    logger.info("✓ Database tables created successfully")

def drop_all_tables():
    """
    Supprime toutes les tables (ATTENTION: données perdues!).
    À utiliser UNIQUEMENT en développement.
    """
    logger.warning("⚠️  DROPPING ALL TABLES - DATA WILL BE LOST!")
    Base.metadata.drop_all(bind=engine)
    logger.warning("✓ All tables dropped")

def test_connection():
    """
    Teste la connexion à la base de données.
    """
    try:
        with engine.connect() as connection:
            result = connection.execute(text("SELECT 1"))
            logger.info("✓ Database connection successful")
            return True
    except Exception as e:
        logger.error(f"✗ Database connection failed: {e}")
        return False

# ============================================================
# IMPORTS DANS VOS MODÈLES:
# ============================================================
# from backend.database import Base
# from sqlalchemy import Column, Integer, String
# 
# class User(Base):
#     __tablename__ = "users"
#     id = Column(Integer, primary_key=True)
#     email = Column(String, unique=True)
#
# IMPORTS DANS VOS ROUTERS:
# from fastapi import Depends
# from sqlalchemy.orm import Session
# from backend.database import get_db
#
# @app.get("/users")
# def list_users(db: Session = Depends(get_db)):
#     return db.query(User).all()
#
# MIGRATION INITIAL (si pas de script SQL pré-fourni):
# python -c "from backend.database import create_all_tables; create_all_tables()"
#
# TEST DE CONNEXION:
# python -c "from backend.database import test_connection; test_connection()"
# ============================================================

if __name__ == "__main__":
    # Test la connexion au démarrage direct du fichier
    logging.basicConfig(level=logging.INFO)
    test_connection()
