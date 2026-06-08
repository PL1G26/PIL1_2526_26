# ============================================================
# IFRI_MentorLink — Skills Router
# backend/routers/skills.py
# Endpoints: /api/skills (GET)
# ============================================================

from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import text

from database import get_db
from routers.auth import get_current_user
from models.user import User
from schemas.user_schema import SkillResponse


# ──── ROUTER CONFIGURATION ───────────────────────────────────
router = APIRouter()


# ──── SKILLS ENDPOINTS ────────────────────────────────────────
@router.get(
    "/",
    response_model=List[SkillResponse],
    summary="Lister toutes les compétences disponibles",
)
async def get_all_skills(
    db: Session = Depends(get_db),
) -> List[SkillResponse]:
    """
    Retourne la liste de toutes les compétences/matières disponibles
    sur la plateforme. Cette liste est pré-remplie avec les matières IFRI.
    
    Accessible sans authentification.
    """
    query = text("""
        SELECT id, name 
        FROM skills 
        ORDER BY name
    """)
    result = db.execute(query).fetchall()
    
    return [
        SkillResponse(id=row.id, name=row.name)
        for row in result
    ]


@router.get(
    "/{skill_id}",
    response_model=SkillResponse,
    summary="Récupérer une compétence par son ID",
)
async def get_skill_by_id(
    skill_id: int,
    db: Session = Depends(get_db),
) -> SkillResponse:
    """
    Retourne les détails d'une compétence spécifique par son ID.
    
    Accessible sans authentification.
    """
    query = text("""
        SELECT id, name 
        FROM skills 
        WHERE id = :skill_id
    """)
    result = db.execute(query, {"skill_id": skill_id}).fetchone()
    
    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Compétence non trouvée",
        )
    
    return SkillResponse(id=result.id, name=result.name)