# ============================================================
# IFRI_MentorLink — Database Initialization Script
# Crée toutes les tables et données initiales
# ============================================================

import logging
from database import create_all_tables, test_connection, engine
from config import settings

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

def init_db():
    """
    Initialise la base de données:
    1. Test la connexion
    2. Crée les tables via SQLAlchemy
    3. Pré-remplit les données de référence (skills)
    """
    
    logger.info("=" * 60)
    logger.info("IFRI_MentorLink — Database Initialization")
    logger.info("=" * 60)
    
    # 1. Test connection
    logger.info("\n1️⃣  Testing database connection...")
    if not test_connection():
        logger.error("❌ Cannot connect to database. Check DATABASE_URL in .env")
        return False
    
    # 2. Create tables
    logger.info("\n2️⃣  Creating database tables...")
    try:
        create_all_tables()
        logger.info("✓ Database tables created successfully")
    except Exception as e:
        logger.error(f"❌ Error creating tables: {e}")
        return False
    
    # 3. Seed initial data
    logger.info("\n3️⃣  Seeding reference data (skills)...")
    try:
        from database import SessionLocal
        from sqlalchemy import text
        
        db = SessionLocal()
        
        # Check if skills already exist
        result = db.execute(text("SELECT COUNT(*) FROM skills"))
        count = result.scalar()
        
        if count > 0:
            logger.info(f"✓ Skills already exist ({count} entries) - skipping seed")
        else:
            logger.info("No skills found - inserting initial data...")
            
            # Insert initial skills
            skills_data = [
                "Algorithmique",
                "Structures de données",
                "Programmation Python",
                "Développement Web (HTML/CSS)",
                "JavaScript",
                "Vue.js",
                "Bases de données SQL",
                "Algèbre relationnelle",
                "Modélisation de bases de données",
                "Réseaux informatiques",
                "Systèmes d'exploitation Linux",
                "Mathématiques discrètes",
                "Intelligence Artificielle",
                "Probabilités et statistiques",
                "FastAPI / Flask / Django"
            ]
            
            for skill in skills_data:
                db.execute(text(f"INSERT INTO skills (name) VALUES ('{skill}')"))
            
            db.commit()
            logger.info(f"✓ Inserted {len(skills_data)} skills")
        
        db.close()
    except Exception as e:
        logger.error(f"⚠️  Error seeding skills: {e} (non-critical)")
    
    logger.info("\n" + "=" * 60)
    logger.info("✓ Database initialization complete!")
    logger.info("=" * 60)
    logger.info(f"\nDatabase: {settings.database_url.split('@')[1] if '@' in settings.database_url else 'N/A'}")
    logger.info(f"Environment: {settings.env}")
    logger.info("\nYou can now start the API with:")
    logger.info("  uvicorn main:app --reload")
    
    return True

if __name__ == "__main__":
    success = init_db()
    exit(0 if success else 1)
