from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from supabase import create_client, Client 

from config import DATABASE_URL, SUPABASE_URL, SUPABASE_KEY

# ── Client Supabase ───────────────────────────────────────────
# Utilisé pour le Realtime (notifications chat temps réel)
# Ce client parle à Supabase via son API REST
supabase: Client = create_client(SUPABASE_URL or "", SUPABASE_KEY or "")

# ── SQLAlchemy (connexion PostgreSQL directe) ─────────────────
# Utilisé par tous les routers pour les opérations CRUD
# C'est cette connexion que tous nos models utilisent
engine = create_engine(DATABASE_URL or "", pool_pre_ping=True)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    """
    Dépendance FastAPI injectée dans chaque router.
    Ouvre une session SQLAlchemy, la donne au router,
    puis la ferme proprement même en cas d'erreur.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()