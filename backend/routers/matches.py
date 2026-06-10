# ============================================================
# IFRI_MentorLink — Matches Router
# backend/routers/matches.py
# Endpoints: /api/matches (GET, accept, reject)
# ============================================================

from typing import Any, Dict, List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import text

from database import get_db
from models.user import User
from routers.auth import get_current_user
from schemas.match_schema import (
    AcceptMatchResponse,
    MatchListResponse,
    MatchResponse,
    RejectMatchResponse,
)
from services.matching_service import compute_matches_for_user


# ──── ROUTER CONFIGURATION ───────────────────────────────────
router = APIRouter()


# ──── HELPER FUNCTIONS ───────────────────────────────────────
def _get_match_with_details(db: Session, match_id: int) -> Dict[str, Any]:
    """Récupère un match avec les détails du mentor, mentoré et compétence."""
    query = text("""
        SELECT 
            m.id, m.mentor_id, m.mentee_id, m.offer_post_id, m.request_post_id,
            m.skill_id, m.score, m.status, m.created_at,
            mentor.id as mentor_id, mentor.first_name as mentor_first_name, 
            mentor.last_name as mentor_last_name, mentor.profile_photo as mentor_photo,
            mentor.field_of_study as mentor_field, mentor.level as mentor_level,
            mentee.id as mentee_id, mentee.first_name as mentee_first_name,
            mentee.last_name as mentee_last_name, mentee.profile_photo as mentee_photo,
            mentee.field_of_study as mentee_field, mentee.level as mentee_level,
            s.id as skill_id, s.name as skill_name
        FROM matches m
        JOIN users mentor ON m.mentor_id = mentor.id
        JOIN users mentee ON m.mentee_id = mentee.id
        LEFT JOIN skills s ON m.skill_id = s.id
        WHERE m.id = :match_id
    """)
    result = db.execute(query, {"match_id": match_id}).fetchone()
    
    if not result:
        return None
    
    return {
        "id": result.id,
        "mentor_id": result.mentor_id,
        "mentee_id": result.mentee_id,
        "offer_post_id": result.offer_post_id,
        "request_post_id": result.request_post_id,
        "skill_id": result.skill_id,
        "score": float(result.score),
        "status": result.status,
        "created_at": result.created_at,
        "mentor": {
            "id": result.mentor_id,
            "first_name": result.mentor_first_name,
            "last_name": result.mentor_last_name,
            "profile_photo": result.mentor_photo,
            "field_of_study": result.mentor_field,
            "level": result.mentor_level,
        },
        "mentee": {
            "id": result.mentee_id,
            "first_name": result.mentee_first_name,
            "last_name": result.mentee_last_name,
            "profile_photo": result.mentee_photo,
            "field_of_study": result.mentee_field,
            "level": result.mentee_level,
        },
        "skill": {
            "id": result.skill_id,
            "name": result.skill_name,
        } if result.skill_id else None,
    }


def _build_match_response(match_data: Dict[str, Any]) -> MatchResponse:
    """Construit la réponse MatchResponse."""
    return MatchResponse(
        id=match_data["id"],
        mentor_id=match_data["mentor_id"],
        mentee_id=match_data["mentee_id"],
        mentor=match_data["mentor"],
        mentee=match_data["mentee"],
        offer_post_id=match_data.get("offer_post_id"),
        request_post_id=match_data.get("request_post_id"),
        skill_id=match_data["skill_id"],
        skill=match_data["skill"],
        score=match_data["score"],
        status=match_data["status"],
        created_at=match_data["created_at"],
    )


# ──── MATCHES ENDPOINTS ───────────────────────────────────────
@router.get(
    "/",
    response_model=MatchListResponse,
    summary="Obtenir mes correspondances calculées",
)
async def get_my_matches(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> MatchListResponse:
    """
    Calcule et retourne les correspondances pour l'utilisateur connecté.
    Les matches sont triés par score décroissant.
    """
    # Calculer les matches
    computed_matches = compute_matches_for_user(db, current_user.id)
    
    # Récupérer tous les matches existants pour cet utilisateur en une seule requête
    existing_query = text("""
        SELECT mentor_id, mentee_id, skill_id 
        FROM matches 
        WHERE mentor_id = :user_id OR mentee_id = :user_id
    """)
    existing_rows = db.execute(existing_query, {"user_id": current_user.id}).fetchall()
    existing_set = {(row.mentor_id, row.mentee_id, row.skill_id) for row in existing_rows}
    
    new_matches = []
    for match_data in computed_matches:
        key = (match_data["mentor_id"], match_data["mentee_id"], match_data["skill_id"])
        if key not in existing_set:
            new_matches.append(match_data)
            existing_set.add(key)
            
    if new_matches:
        insert_query = text("""
            INSERT INTO matches (mentor_id, mentee_id, skill_id, score, status, created_at)
            VALUES (:mentor_id, :mentee_id, :skill_id, :score, :status, :created_at)
        """)
        db.execute(insert_query, new_matches)
        db.commit()
    
    # Récupérer les matches de l'utilisateur (où il est mentor ou mentoré)
    query = text("""
        SELECT 
            m.id, m.mentor_id, m.mentee_id, m.offer_post_id, m.request_post_id,
            m.skill_id, m.score, m.status, m.created_at,
            mentor.id as m_id, mentor.first_name as m_fname, mentor.last_name as m_lname,
            mentor.profile_photo as m_photo, mentor.field_of_study as m_field, mentor.level as m_level,
            mentee.id as e_id, mentee.first_name as e_fname, mentee.last_name as e_lname,
            mentee.profile_photo as e_photo, mentee.field_of_study as e_field, mentee.level as e_level,
            s.id as s_id, s.name as s_name
        FROM matches m
        JOIN users mentor ON m.mentor_id = mentor.id
        JOIN users mentee ON m.mentee_id = mentee.id
        LEFT JOIN skills s ON m.skill_id = s.id
        WHERE m.mentor_id = :user_id OR m.mentee_id = :user_id
        ORDER BY m.score DESC
    """)
    result = db.execute(query, {"user_id": current_user.id}).fetchall()
    
    matches = []
    for row in result:
        match_data = {
            "id": row.id,
            "mentor_id": row.mentor_id,
            "mentee_id": row.mentee_id,
            "offer_post_id": row.offer_post_id,
            "request_post_id": row.request_post_id,
            "skill_id": row.skill_id,
            "score": float(row.score),
            "status": row.status,
            "created_at": row.created_at,
            "mentor": {
                "id": row.m_id,
                "first_name": row.m_fname,
                "last_name": row.m_lname,
                "profile_photo": row.m_photo,
                "field_of_study": row.m_field,
                "level": row.m_level,
            },
            "mentee": {
                "id": row.e_id,
                "first_name": row.e_fname,
                "last_name": row.e_lname,
                "profile_photo": row.e_photo,
                "field_of_study": row.e_field,
                "level": row.e_level,
            },
            "skill": {
                "id": row.s_id,
                "name": row.s_name,
            } if row.s_id else None,
        }
        matches.append(_build_match_response(match_data))
    
    return MatchListResponse(matches=matches, total=len(matches))


@router.put(
    "/{match_id}/accept",
    response_model=AcceptMatchResponse,
    summary="Accepter un match",
)
async def accept_match(
    match_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> AcceptMatchResponse:
    """
    Accepte un match. Crée automatiquement une conversation.
    """
    # Vérifier que le match existe
    match = _get_match_with_details(db, match_id)
    
    if not match:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Match non trouvé",
        )
    
    # Vérifier que l'utilisateur est impliqué dans le match
    if current_user.id != match["mentor_id"] and current_user.id != match["mentee_id"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Vous n'êtes pas autorisé à accepter ce match",
        )
    
    # Vérifier que le match est en attente
    if match["status"] != "pending":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Ce match a déjà été {match['status']}",
        )
    
    # Mettre à jour le statut du match
    update_query = text("""
        UPDATE matches SET status = 'accepted' WHERE id = :match_id
    """)
    db.execute(update_query, {"match_id": match_id})
    db.commit()
    
    # Créer la conversation
    insert_conv = text("""
        INSERT INTO conversations (match_id)
        VALUES (:match_id)
        RETURNING id
    """)
    result = db.execute(insert_conv, {"match_id": match_id})
    # Lire le résultat AVANT le commit : psycopg2 ferme le curseur après commit
    conversation_id = result.fetchone().id
    db.commit()
    
    return AcceptMatchResponse(
        message="Match accepté avec succès",
        match_id=match_id,
        conversation_id=conversation_id,
    )


@router.put(
    "/{match_id}/reject",
    response_model=RejectMatchResponse,
    summary="Refuser un match",
)
async def reject_match(
    match_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> RejectMatchResponse:
    """
    Refuse un match.
    """
    # Vérifier que le match existe
    match = _get_match_with_details(db, match_id)
    
    if not match:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Match non trouvé",
        )
    
    # Vérifier que l'utilisateur est impliqué dans le match
    if current_user.id != match["mentor_id"] and current_user.id != match["mentee_id"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Vous n'êtes pas autorisé à refuser ce match",
        )
    
    # Vérifier que le match est en attente
    if match["status"] != "pending":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Ce match a déjà été {match['status']}",
        )
    
    # Mettre à jour le statut du match
    update_query = text("""
        UPDATE matches SET status = 'rejected' WHERE id = :match_id
    """)
    db.execute(update_query, {"match_id": match_id})
    db.commit()
    
    return RejectMatchResponse(
        message="Match refusé",
        match_id=match_id,
    )