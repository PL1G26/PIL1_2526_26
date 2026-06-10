# ============================================================
# IFRI_MentorLink — Users Router
# backend/routers/users.py
# Endpoints: /api/users/me (GET/PUT), skills, availabilities
# ============================================================

from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import text

from database import get_db
from models.user import User
from routers.auth import get_current_user
from schemas.user_schema import (
    AddAvailabilityRequest,
    AddSkillRequest,
    AvailabilityResponse,
    SkillResponse,
    UpdateProfileRequest,
    UserBasicResponse,
    UserProfileResponse,
    UserSkillResponse,
)


# ──── ROUTER CONFIGURATION ───────────────────────────────────
router = APIRouter()


# ──── HELPER FUNCTIONS ───────────────────────────────────────
def _get_user_skills(db: Session, user_id: int) -> List[Dict[str, Any]]:
    """Récupère les compétences d'un utilisateur avec les infos de la compétence."""
    query = text("""
        SELECT us.user_id, us.skill_id, us.proficiency, s.name as skill_name
        FROM user_skills us
        JOIN skills s ON us.skill_id = s.id
        WHERE us.user_id = :user_id
    """)
    result = db.execute(query, {"user_id": user_id}).fetchall()
    return [
        {
            "skill_id": row.skill_id,
            "skill": {"id": row.skill_id, "name": row.skill_name},
            "proficiency": row.proficiency,
        }
        for row in result
    ]


def _get_user_availabilities(db: Session, user_id: int) -> List[Dict[str, Any]]:
    """Récupère les disponibilités d'un utilisateur."""
    query = text("""
        SELECT id, day_of_week, start_time, end_time
        FROM user_availabilities
        WHERE user_id = :user_id
        ORDER BY 
            CASE day_of_week
                WHEN 'Monday' THEN 1
                WHEN 'Tuesday' THEN 2
                WHEN 'Wednesday' THEN 3
                WHEN 'Thursday' THEN 4
                WHEN 'Friday' THEN 5
                WHEN 'Saturday' THEN 6
                WHEN 'Sunday' THEN 7
            END,
            start_time
    """)
    result = db.execute(query, {"user_id": user_id}).fetchall()
    return [
        {
            "id": row.id,
            "day_of_week": row.day_of_week,
            "start_time": str(row.start_time),
            "end_time": str(row.end_time),
        }
        for row in result
    ]


# ──── USER PROFILE ENDPOINTS ─────────────────────────────────
@router.get(
    "/me",
    response_model=UserProfileResponse,
    summary="Récupérer le profil de l'utilisateur connecté",
)
async def get_current_user_profile(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> UserProfileResponse:
    """
    Retourne le profil complet de l'utilisateur connecté,
    y compris ses compétences et disponibilités.
    """
    # Récupérer les compétences
    skills = _get_user_skills(db, current_user.id)
    
    # Récupérer les disponibilités
    availabilities = _get_user_availabilities(db, current_user.id)
    
    return UserProfileResponse(
        id=current_user.id,
        first_name=current_user.first_name,
        last_name=current_user.last_name,
        email=current_user.email,
        phone_number=current_user.phone_number,
        profile_photo=current_user.profile_photo,
        field_of_study=current_user.field_of_study,
        level=current_user.level,
        bio=current_user.bio,
        created_at=current_user.created_at,
        updated_at=current_user.updated_at,
        skills=[UserSkillResponse(**s) for s in skills],
        availabilities=[AvailabilityResponse(**a) for a in availabilities],
    )


@router.get(
    "/{user_id}",
    response_model=UserProfileResponse,
    summary="Récupérer le profil d'un autre utilisateur",
)
async def get_user_profile(
    user_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> UserProfileResponse:
    """
    Retourne le profil complet d'un utilisateur,
    y compris ses compétences et disponibilités.
    """
    user_query = text("SELECT * FROM users WHERE id = :user_id")
    target_user = db.execute(user_query, {"user_id": user_id}).fetchone()
    
    if not target_user:
        raise HTTPException(status_code=404, detail="Utilisateur non trouvé")
    
    skills = _get_user_skills(db, user_id)
    availabilities = _get_user_availabilities(db, user_id)
    
    return UserProfileResponse(
        id=target_user.id,
        first_name=target_user.first_name,
        last_name=target_user.last_name,
        email=target_user.email,
        phone_number=target_user.phone_number,
        profile_photo=target_user.profile_photo,
        field_of_study=target_user.field_of_study,
        level=target_user.level,
        bio=target_user.bio,
        created_at=target_user.created_at,
        updated_at=target_user.updated_at,
        skills=[UserSkillResponse(**s) for s in skills],
        availabilities=[AvailabilityResponse(**a) for a in availabilities],
    )


@router.put(
    "/me",
    response_model=UserBasicResponse,
    summary="Mettre à jour le profil utilisateur",
)
async def update_current_user_profile(
    updates: UpdateProfileRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> UserBasicResponse:
    """
    Met à jour les informations du profil de l'utilisateur connecté.
    Seuls les champs fournis seront mis à jour.
    """
    # Construire le dictionnaire des champs à mettre à jour
    update_data = {}
    if updates.first_name is not None:
        update_data["first_name"] = updates.first_name
    if updates.last_name is not None:
        update_data["last_name"] = updates.last_name
    if updates.profile_photo is not None:
        update_data["profile_photo"] = updates.profile_photo
    if updates.field_of_study is not None:
        update_data["field_of_study"] = updates.field_of_study
    if updates.level is not None:
        update_data["level"] = updates.level
    if updates.bio is not None:
        update_data["bio"] = updates.bio
    
    if not update_data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Aucun champ à mettre à jour",
        )
    
    # Mettre à jour l'utilisateur
    for key, value in update_data.items():
        setattr(current_user, key, value)
    
    db.commit()
    db.refresh(current_user)
    
    return UserBasicResponse(
        id=current_user.id,
        first_name=current_user.first_name,
        last_name=current_user.last_name,
        profile_photo=current_user.profile_photo,
        field_of_study=current_user.field_of_study,
        level=current_user.level,
    )


# ──── USER SKILLS ENDPOINTS ──────────────────────────────────
@router.post(
    "/me/skills",
    status_code=status.HTTP_201_CREATED,
    summary="Ajouter une compétence au profil",
)
async def add_user_skill(
    skill_data: AddSkillRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Dict[str, Any]:
    """
    Ajoute une compétence au profil de l'utilisateur.
    - proficiency = 'strong' : point fort (peut enseigner)
    - proficiency = 'weak' : lacune (a besoin d'aide)
    """
    # Vérifier que la compétence existe
    skill_check = text("SELECT id, name FROM skills WHERE id = :skill_id")
    skill = db.execute(skill_check, {"skill_id": skill_data.skill_id}).fetchone()
    
    if not skill:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Compétence non trouvée",
        )
    
    # Vérifier si l'utilisateur a déjà cette compétence
    existing = text("""
        SELECT user_id, skill_id FROM user_skills 
        WHERE user_id = :user_id AND skill_id = :skill_id
    """)
    existing_result = db.execute(existing, {
        "user_id": current_user.id,
        "skill_id": skill_data.skill_id
    }).fetchone()
    
    if existing_result:
        # Mettre à jour le proficiency existant
        update_query = text("""
            UPDATE user_skills 
            SET proficiency = :proficiency
            WHERE user_id = :user_id AND skill_id = :skill_id
        """)
        db.execute(update_query, {
            "user_id": current_user.id,
            "skill_id": skill_data.skill_id,
            "proficiency": skill_data.proficiency
        })
        db.commit()
    else:
        # Insérer la nouvelle compétence
        insert_query = text("""
            INSERT INTO user_skills (user_id, skill_id, proficiency)
            VALUES (:user_id, :skill_id, :proficiency)
        """)
        db.execute(insert_query, {
            "user_id": current_user.id,
            "skill_id": skill_data.skill_id,
            "proficiency": skill_data.proficiency
        })
        db.commit()
    
    return {
        "message": "Compétence ajoutée avec succès",
        "skill_id": skill_data.skill_id,
        "skill_name": skill.name,
        "proficiency": skill_data.proficiency,
    }


@router.delete(
    "/me/skills/{skill_id}",
    status_code=status.HTTP_200_OK,
    summary="Supprimer une compétence du profil",
)
async def remove_user_skill(
    skill_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Dict[str, str]:
    """
    Supprime une compétence du profil de l'utilisateur.
    """
    # Vérifier si la compétence existe pour cet utilisateur
    check_query = text("""
        SELECT user_id, skill_id FROM user_skills 
        WHERE user_id = :user_id AND skill_id = :skill_id
    """)
    existing = db.execute(check_query, {
        "user_id": current_user.id,
        "skill_id": skill_id
    }).fetchone()
    
    if not existing:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cette compétence n'existe pas dans votre profil",
        )
    
    # Supprimer la compétence
    delete_query = text("""
        DELETE FROM user_skills 
        WHERE user_id = :user_id AND skill_id = :skill_id
    """)
    db.execute(delete_query, {
        "user_id": current_user.id,
        "skill_id": skill_id
    })
    db.commit()
    
    return {"message": "Compétence supprimée avec succès"}


# ──── USER AVAILABILITIES ENDPOINTS ────────────────────────────
@router.post(
    "/me/availabilities",
    status_code=status.HTTP_201_CREATED,
    summary="Ajouter un créneau de disponibilité",
)
async def add_user_availability(
    availability: AddAvailabilityRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Dict[str, Any]:
    """
    Ajoute un créneau de disponibilité au profil de l'utilisateur.
    """
    # Insérer la disponibilité
    insert_query = text("""
        INSERT INTO user_availabilities (user_id, day_of_week, start_time, end_time)
        VALUES (:user_id, :day_of_week, :start_time, :end_time)
        RETURNING id
    """)
    result = db.execute(insert_query, {
        "user_id": current_user.id,
        "day_of_week": availability.day_of_week,
        "start_time": availability.start_time,
        "end_time": availability.end_time,
    })
    # Lire le résultat AVANT le commit : psycopg2 ferme le curseur après commit
    new_id = result.scalar_one()
    db.commit()
    
    return {
        "message": "Disponibilité ajoutée avec succès",
        "id": new_id,
        "day_of_week": availability.day_of_week,
        "start_time": availability.start_time,
        "end_time": availability.end_time,
    }


@router.delete(
    "/me/availabilities/{availability_id}",
    status_code=status.HTTP_200_OK,
    summary="Supprimer un créneau de disponibilité",
)
async def remove_user_availability(
    availability_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Dict[str, str]:
    """
    Supprime un créneau de disponibilité du profil de l'utilisateur.
    """
    # Vérifier que la disponibilité appartient à l'utilisateur
    check_query = text("""
        SELECT id, user_id FROM user_availabilities 
        WHERE id = :availability_id AND user_id = :user_id
    """)
    existing = db.execute(check_query, {
        "availability_id": availability_id,
        "user_id": current_user.id
    }).fetchone()
    
    if not existing:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cette disponibilité n'existe pas dans votre profil",
        )
    
    # Supprimer la disponibilité
    delete_query = text("""
        DELETE FROM user_availabilities 
        WHERE id = :availability_id
    """)
    db.execute(delete_query, {"availability_id": availability_id})
    db.commit()
    
    return {"message": "Disponibilité supprimée avec succès"}


@router.get(
    "/me/availabilities",
    response_model=List[AvailabilityResponse],
    summary="Lister les disponibilités de l'utilisateur",
)
async def list_user_availabilities(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> List[AvailabilityResponse]:
    """
    Liste tous les créneaux de disponibilité de l'utilisateur connecté.
    """
    availabilities = _get_user_availabilities(db, current_user.id)
    return [AvailabilityResponse(**a) for a in availabilities]