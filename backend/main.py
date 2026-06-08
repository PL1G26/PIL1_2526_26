from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from database import get_db

from routers import auth, users, skills, posts, matches, chat

app = FastAPI(
    title="IFRI MentorLink API",
    version="1.0.0"
)

from fastapi import Request
from fastapi.responses import JSONResponse

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    import traceback
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal Server Error", "traceback": traceback.format_exc()}
    )



# ── CORS ─────────────────────────────────────────────────────
# Autorise Vue.js (qui tourne sur localhost:5173) à appeler l'API
# En production, remplacer "*" par l'URL réelle du frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── ROUTERS ──────────────────────────────────────────────────
# Chaque router gère un domaine fonctionnel
# Le préfixe /api est ajouté devant toutes les routes
app.include_router(auth.router,    prefix="/api/auth",          tags=["Auth"])
app.include_router(users.router,   prefix="/api/users",         tags=["Utilisateurs"])
app.include_router(skills.router,  prefix="/api/skills",        tags=["Compétences"])
app.include_router(posts.router,   prefix="/api/posts",         tags=["Posts"])
app.include_router(matches.router, prefix="/api/matches",       tags=["Matching"])
app.include_router(chat.router,    prefix="/api",               tags=["Messagerie"])


@app.get("/")
def root():
    return {"message": "IFRI MentorLink API — opérationnelle ✅"}

# Dans main.py, ajouter temporairement
@app.get("/test-db")
def test_db(db: Session = Depends(get_db)):
    from sqlalchemy import text
    result = db.execute(text("SELECT 1")).fetchone()
    return {"db_connected": result is not None}