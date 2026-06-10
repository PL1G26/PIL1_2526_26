# ============================================================
# IFRI_MentorLink — Posts Router
# backend/routers/posts.py
# Endpoints: CRUD posts de mentorat
# ============================================================

from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import text

from database import get_db
from models.user import User
from routers.auth import get_current_user
from schemas.post_schema import (
    CreatePostRequest,
    PostResponse,
    UpdatePostRequest,
)


# ──── ROUTER CONFIGURATION ───────────────────────────────────
router = APIRouter()


# ──── HELPER FUNCTIONS ───────────────────────────────────────
def _get_post_with_details(db: Session, post_id: int) -> Optional[Dict[str, Any]]:
    """Récupère un post avec les détails de l'utilisateur et de la compétence."""
    query = text("""
        SELECT 
            mp.id, mp.user_id, mp.type, mp.skill_id, mp.mode,
            mp.description, mp.is_active, mp.created_at, mp.updated_at,
            u.id as user_id, u.first_name, u.last_name, u.profile_photo,
            u.field_of_study, u.level,
            s.id as skill_id, s.name as skill_name
        FROM mentorship_posts mp
        JOIN users u ON mp.user_id = u.id
        JOIN skills s ON mp.skill_id = s.id
        WHERE mp.id = :post_id
    """)
    result = db.execute(query, {"post_id": post_id}).fetchone()
    
    if not result:
        return None
    
    return {
        "id": result.id,
        "user_id": result.user_id,
        "type": result.type,
        "skill_id": result.skill_id,
        "mode": result.mode,
        "description": result.description,
        "is_active": result.is_active,
        "created_at": result.created_at,
        "updated_at": result.updated_at,
        "user": {
            "id": result.user_id,
            "first_name": result.first_name,
            "last_name": result.last_name,
            "profile_photo": result.profile_photo,
            "field_of_study": result.field_of_study,
            "level": result.level,
        },
        "skill": {
            "id": result.skill_id,
            "name": result.skill_name,
        },
    }


def _get_post_availabilities(db: Session, post_id: int) -> List[Dict[str, Any]]:
    """Récupère les disponibilités d'un post."""
    query = text("""
        SELECT id, day_of_week, start_time, end_time
        FROM post_availabilities
        WHERE post_id = :post_id
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
    result = db.execute(query, {"post_id": post_id}).fetchall()
    return [
        {
            "id": row.id,
            "day_of_week": row.day_of_week,
            "start_time": str(row.start_time),
            "end_time": str(row.end_time),
        }
        for row in result
    ]


def _build_post_response(db: Session, post_data: Dict[str, Any]) -> PostResponse:
    """Construit la réponse complète d'un post avec ses disponibilités."""
    availabilities = _get_post_availabilities(db, post_data["id"])
    
    if not availabilities:
        # Fallback : utiliser les disponibilités du profil de l'utilisateur
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
        result = db.execute(query, {"user_id": post_data["user_id"]}).fetchall()
        availabilities = [
            {
                "id": row.id,
                "day_of_week": row.day_of_week,
                "start_time": str(row.start_time),
                "end_time": str(row.end_time),
            }
            for row in result
        ]
    
    return PostResponse(
        id=post_data["id"],
        user_id=post_data["user_id"],
        type=post_data["type"],
        skill_id=post_data["skill_id"],
        mode=post_data["mode"],
        description=post_data["description"],
        is_active=post_data["is_active"],
        created_at=post_data["created_at"],
        updated_at=post_data["updated_at"],
        user=post_data["user"],
        skill=post_data["skill"],
        availabilities=availabilities,
    )


# ──── POSTS ENDPOINTS ────────────────────────────────────────
@router.get(
    "/",
    response_model=List[PostResponse],
    summary="Lister tous les posts actifs",
)
async def get_all_posts(
    skill_id: Optional[int] = None,
    post_type: Optional[str] = None,
    mode: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> List[PostResponse]:
    """
    Liste tous les posts actifs.
    """
    query_str = """
        SELECT 
            mp.id, mp.user_id, mp.type, mp.skill_id, mp.mode,
            mp.description, mp.is_active, mp.created_at, mp.updated_at,
            u.id as u_id, u.first_name, u.last_name, u.profile_photo,
            u.field_of_study, u.level,
            s.id as s_id, s.name as skill_name
        FROM mentorship_posts mp
        JOIN users u ON mp.user_id = u.id
        JOIN skills s ON mp.skill_id = s.id
        WHERE mp.is_active = TRUE
    """
    
    params = {}
    if skill_id:
        query_str += " AND mp.skill_id = :skill_id"
        params["skill_id"] = skill_id
    if post_type:
        query_str += " AND mp.type = :post_type"
        params["post_type"] = post_type
    if mode:
        query_str += " AND mp.mode = :mode"
        params["mode"] = mode
    
    query_str += " ORDER BY mp.created_at DESC"
    
    result = db.execute(text(query_str), params).fetchall()
    
    if not result:
        return []

    post_ids = [row.id for row in result]
    user_ids = list(set([row.user_id for row in result]))

    # Fetch all post availabilities
    post_avails_query = text("""
        SELECT id, post_id, day_of_week, start_time, end_time
        FROM post_availabilities
        WHERE post_id = ANY(:post_ids)
        ORDER BY 
            CASE day_of_week
                WHEN 'Monday' THEN 1 WHEN 'Tuesday' THEN 2 WHEN 'Wednesday' THEN 3
                WHEN 'Thursday' THEN 4 WHEN 'Friday' THEN 5 WHEN 'Saturday' THEN 6 WHEN 'Sunday' THEN 7
            END, start_time
    """)
    p_avails = db.execute(post_avails_query, {"post_ids": post_ids}).fetchall()
    
    post_avail_map = {}
    for pa in p_avails:
        post_avail_map.setdefault(pa.post_id, []).append({
            "id": pa.id,
            "day_of_week": pa.day_of_week,
            "start_time": str(pa.start_time),
            "end_time": str(pa.end_time),
        })

    # Fetch user availabilities for fallback
    user_avails_query = text("""
        SELECT id, user_id, day_of_week, start_time, end_time
        FROM user_availabilities
        WHERE user_id = ANY(:user_ids)
        ORDER BY 
            CASE day_of_week
                WHEN 'Monday' THEN 1 WHEN 'Tuesday' THEN 2 WHEN 'Wednesday' THEN 3
                WHEN 'Thursday' THEN 4 WHEN 'Friday' THEN 5 WHEN 'Saturday' THEN 6 WHEN 'Sunday' THEN 7
            END, start_time
    """)
    u_avails = db.execute(user_avails_query, {"user_ids": user_ids}).fetchall()
    
    user_avail_map = {}
    for ua in u_avails:
        user_avail_map.setdefault(ua.user_id, []).append({
            "id": ua.id,
            "day_of_week": ua.day_of_week,
            "start_time": str(ua.start_time),
            "end_time": str(ua.end_time),
        })
    
    posts = []
    for row in result:
        avails = post_avail_map.get(row.id, [])
        if not avails:
            avails = user_avail_map.get(row.user_id, [])

        posts.append(PostResponse(
            id=row.id,
            user_id=row.user_id,
            type=row.type,
            skill_id=row.skill_id,
            mode=row.mode,
            description=row.description,
            is_active=row.is_active,
            created_at=row.created_at,
            updated_at=row.updated_at,
            user={
                "id": row.u_id,
                "first_name": row.first_name,
                "last_name": row.last_name,
                "profile_photo": row.profile_photo,
                "field_of_study": row.field_of_study,
                "level": row.level,
            },
            skill={
                "id": row.s_id,
                "name": row.skill_name,
            },
            availabilities=avails
        ))
    
    return posts


@router.post(
    "/",
    response_model=PostResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Créer un nouveau post",
)
async def create_post(
    post_data: CreatePostRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> PostResponse:
    """
    Crée un nouveau post de mentorat (offre ou demande).
    """
    # Vérifier que la compétence existe
    skill_check = text("SELECT id, name FROM skills WHERE id = :skill_id")
    skill = db.execute(skill_check, {"skill_id": post_data.skill_id}).fetchone()
    
    if not skill:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Compétence non trouvée",
        )
    
    # Créer le post
    insert_query = text("""
        INSERT INTO mentorship_posts (user_id, type, skill_id, mode, description)
        VALUES (:user_id, :type, :skill_id, :mode, :description)
        RETURNING id, user_id, type, skill_id, mode, description, is_active, created_at, updated_at
    """)
    result = db.execute(insert_query, {
        "user_id": current_user.id,
        "type": post_data.type,
        "skill_id": post_data.skill_id,
        "mode": post_data.mode,
        "description": post_data.description,
    })
    # Lire le résultat AVANT le commit : psycopg2 ferme le curseur après commit
    row = result.fetchone()
    db.commit()
    
    # Récupérer les détails du post créé
    post = _get_post_with_details(db, row.id)
    
    # Ajouter les disponibilités si fournies
    if post_data.availabilities:
        for avail in post_data.availabilities:
            insert_avail = text("""
                INSERT INTO post_availabilities (post_id, day_of_week, start_time, end_time)
                VALUES (:post_id, :day_of_week, :start_time, :end_time)
            """)
            db.execute(insert_avail, {
                "post_id": row.id,
                "day_of_week": avail["day_of_week"],
                "start_time": avail["start_time"],
                "end_time": avail["end_time"],
            })
        db.commit()
    
    # Recharger les disponibilités
    post = _get_post_with_details(db, row.id)
    
    return _build_post_response(db, post)


@router.get(
    "/{post_id}",
    response_model=PostResponse,
    summary="Récupérer un post par son ID",
)
async def get_post(
    post_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> PostResponse:
    """
    Retourne les détails d'un post spécifique.
    """
    post = _get_post_with_details(db, post_id)
    
    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Post non trouvé",
        )
    
    return _build_post_response(db, post)


@router.put(
    "/{post_id}",
    response_model=PostResponse,
    summary="Modifier un post",
)
async def update_post(
    post_id: int,
    updates: UpdatePostRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> PostResponse:
    """
    Modifie un post existant. Seul le propriétaire peut modifier son post.
    """
    # Vérifier que le post existe et appartient à l'utilisateur
    check_query = text("""
        SELECT user_id FROM mentorship_posts WHERE id = :post_id
    """)
    existing = db.execute(check_query, {"post_id": post_id}).fetchone()
    
    if not existing:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Post non trouvé",
        )
    
    if existing.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Vous ne pouvez modifier que vos propres posts",
        )
    
    # Construire les champs à mettre à jour
    update_data = {}
    if updates.skill_id is not None:
        update_data["skill_id"] = updates.skill_id
    if updates.mode is not None:
        update_data["mode"] = updates.mode
    if updates.description is not None:
        update_data["description"] = updates.description
    if updates.is_active is not None:
        update_data["is_active"] = updates.is_active
    
    if update_data:
        # Construire la requête UPDATE
        set_clauses = ", ".join([f"{key} = :{key}" for key in update_data.keys()])
        update_query = text(f"""
            UPDATE mentorship_posts 
            SET {set_clauses}, updated_at = NOW()
            WHERE id = :post_id
        """)
        update_data["post_id"] = post_id
        db.execute(update_query, update_data)
        db.commit()
    
    # Mettre à jour les disponibilités si fournies
    if updates.availabilities is not None:
        # Supprimer les anciennes disponibilités
        delete_avail = text("DELETE FROM post_availabilities WHERE post_id = :post_id")
        db.execute(delete_avail, {"post_id": post_id})
        
        # Insérer les nouvelles disponibilités
        for avail in updates.availabilities:
            insert_avail = text("""
                INSERT INTO post_availabilities (post_id, day_of_week, start_time, end_time)
                VALUES (:post_id, :day_of_week, :start_time, :end_time)
            """)
            db.execute(insert_avail, {
                "post_id": post_id,
                "day_of_week": avail["day_of_week"],
                "start_time": avail["start_time"],
                "end_time": avail["end_time"],
            })
        db.commit()
    
    # Récupérer le post mis à jour
    post = _get_post_with_details(db, post_id)
    
    return _build_post_response(db, post)


@router.delete(
    "/{post_id}",
    status_code=status.HTTP_200_OK,
    summary="Supprimer ou archiver un post",
)
async def delete_post(
    post_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Dict[str, str]:
    """
    Supprime ou archive un post. Seul le propriétaire peut supprimer son post.
    Par défaut, le post est archivé (is_active = FALSE) plutôt que supprimé.
    """
    # Vérifier que le post existe et appartient à l'utilisateur
    check_query = text("""
        SELECT user_id FROM mentorship_posts WHERE id = :post_id
    """)
    existing = db.execute(check_query, {"post_id": post_id}).fetchone()
    
    if not existing:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Post non trouvé",
        )
    
    if existing.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Vous ne pouvez supprimer que vos propres posts",
        )
    
    # Archiver le post (soft delete)
    update_query = text("""
        UPDATE mentorship_posts 
        SET is_active = FALSE, updated_at = NOW()
        WHERE id = :post_id
    """)
    db.execute(update_query, {"post_id": post_id})
    db.commit()
    
    return {"message": "Post archivé avec succès"}