# ============================================================
# IFRI_MentorLink — Chat Router
# backend/routers/chat.py
# Endpoints: conversations, messages
# ============================================================

import asyncio
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import text

from database import get_db
from models.user import User
from routers.auth import get_current_user
from schemas.message_schema import (
    ConversationListResponse,
    ConversationResponse,
    MessageListResponse,
    MessageResponse,
    SendMessageRequest,
    DirectMessageRequest,
    UserBasicResponse,
)


# ──── ROUTER CONFIGURATION ───────────────────────────────────
router = APIRouter()


# ──── HELPER FUNCTIONS ───────────────────────────────────────
def _get_conversation_with_details(db: Session, conversation_id: int) -> Optional[Dict[str, Any]]:
    """Récupère une conversation avec les détails du match."""
    query = text("""
        SELECT 
            c.id, c.match_id, c.created_at, c.updated_at,
            m.mentor_id, m.mentee_id, m.status as match_status
        FROM conversations c
        JOIN matches m ON c.match_id = m.id
        WHERE c.id = :conversation_id
    """)
    result = db.execute(query, {"conversation_id": conversation_id}).fetchone()
    
    if not result:
        return None
    
    return {
        "id": result.id,
        "match_id": result.match_id,
        "mentor_id": result.mentor_id,
        "mentee_id": result.mentee_id,
        "match_status": result.match_status,
        "created_at": result.created_at,
        "updated_at": result.updated_at,
    }


def _get_other_user_in_conversation(
    db: Session, conversation: Dict[str, Any], current_user_id: int
) -> Dict[str, Any]:
    """Récupère l'autre participant à la conversation."""
    other_user_id = (
        conversation["mentee_id"]
        if conversation["mentor_id"] == current_user_id
        else conversation["mentor_id"]
    )
    
    query = text("""
        SELECT id, first_name, last_name, profile_photo
        FROM users WHERE id = :user_id
    """)
    result = db.execute(query, {"user_id": other_user_id}).fetchone()
    
    return {
        "id": result.id,
        "first_name": result.first_name,
        "last_name": result.last_name,
        "profile_photo": result.profile_photo,
    }


def _check_user_in_conversation(
    db: Session, conversation_id: int, current_user_id: int
) -> bool:
    """Vérifie si l'utilisateur est participant à la conversation."""
    conv = _get_conversation_with_details(db, conversation_id)
    if not conv:
        return False
    return current_user_id in [conv["mentor_id"], conv["mentee_id"]]


# ──── CONVERSATIONS ENDPOINTS ────────────────────────────────
@router.get(
    "/conversations",
    response_model=ConversationListResponse,
    summary="Liste de mes conversations",
)
async def get_my_conversations(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> ConversationListResponse:
    """
    Retourne la liste des conversations de l'utilisateur connecté,
    avec le dernier message et le nombre de messages non lus.
    """
    query = text("""
        SELECT 
            c.id, c.match_id, c.created_at, c.updated_at,
            m.mentor_id, m.mentee_id, m.status as match_status,
            u.id as other_id, u.first_name as other_first_name, u.last_name as other_last_name, u.profile_photo as other_profile_photo,
            lm.id as lm_id, lm.sender_id as lm_sender_id, lm.content as lm_content, lm.is_read as lm_is_read, lm.created_at as lm_created_at,
            lms.id as lms_id, lms.first_name as lms_first_name, lms.last_name as lms_last_name, lms.profile_photo as lms_profile_photo,
            (SELECT COUNT(*) FROM messages WHERE conversation_id = c.id AND sender_id != :user_id AND is_read = FALSE) as unread_count
        FROM conversations c
        JOIN matches m ON c.match_id = m.id
        JOIN users u ON u.id = CASE WHEN m.mentor_id = :user_id THEN m.mentee_id ELSE m.mentor_id END
        LEFT JOIN LATERAL (
            SELECT id, sender_id, content, is_read, created_at
            FROM messages
            WHERE conversation_id = c.id
            ORDER BY created_at DESC
            LIMIT 1
        ) lm ON true
        LEFT JOIN users lms ON lms.id = lm.sender_id
        WHERE m.status = 'accepted'
        AND (m.mentor_id = :user_id OR m.mentee_id = :user_id)
        ORDER BY c.updated_at DESC
    """)
    result = db.execute(query, {"user_id": current_user.id}).fetchall()
    
    conversations = []
    for row in result:
        last_message = None
        if row.lm_id:
            last_message = MessageResponse(
                id=row.lm_id,
                conversation_id=row.id,
                sender_id=row.lm_sender_id,
                sender=UserBasicResponse(
                    id=row.lms_id,
                    first_name=row.lms_first_name,
                    last_name=row.lms_last_name,
                    profile_photo=row.lms_profile_photo,
                ),
                content=row.lm_content,
                is_read=row.lm_is_read,
                created_at=row.lm_created_at,
            )
            
        conversations.append(
            ConversationResponse(
                id=row.id,
                match_id=row.match_id,
                other_user=UserBasicResponse(
                    id=row.other_id,
                    first_name=row.other_first_name,
                    last_name=row.other_last_name,
                    profile_photo=row.other_profile_photo,
                ),
                last_message=last_message,
                unread_count=row.unread_count,
                created_at=row.created_at,
                updated_at=row.updated_at,
            )
        )
    
    return ConversationListResponse(conversations=conversations, total=len(conversations))


@router.get(
    "/conversations/{conversation_id}/messages",
    response_model=MessageListResponse,
    summary="Historique des messages d'une conversation",
)
async def get_conversation_messages(
    conversation_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> MessageListResponse:
    """
    Retourne l'historique complet des messages d'une conversation.
    """
    # Vérifier que la conversation existe et que l'utilisateur y participe
    if not _check_user_in_conversation(db, conversation_id, current_user.id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Vous n'êtes pas autorisé à voir cette conversation",
        )
    
    # Récupérer les messages
    query = text("""
        SELECT 
            m.id, m.conversation_id, m.sender_id, m.content, m.is_read, m.created_at,
            u.id as u_id, u.first_name, u.last_name, u.profile_photo
        FROM messages m
        JOIN users u ON m.sender_id = u.id
        WHERE m.conversation_id = :conversation_id
        ORDER BY m.created_at ASC
    """)
    result = db.execute(query, {"conversation_id": conversation_id}).fetchall()
    
    messages = []
    for row in result:
        messages.append(
            MessageResponse(
                id=row.id,
                conversation_id=row.conversation_id,
                sender_id=row.sender_id,
                sender=UserBasicResponse(
                    id=row.u_id,
                    first_name=row.first_name,
                    last_name=row.last_name,
                    profile_photo=row.profile_photo,
                ),
                content=row.content,
                is_read=row.is_read,
                created_at=row.created_at,
            )
        )
    
    return MessageListResponse(messages=messages, total=len(messages))


@router.post(
    "/conversations/{conversation_id}/messages",
    response_model=MessageResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Envoyer un message",
)
async def send_message(
    conversation_id: int,
    message: SendMessageRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> MessageResponse:
    """
    Envoie un message dans une conversation.
    Vérifie que le match associé est accepté.
    """
    # Vérifier que la conversation existe
    conversation = _get_conversation_with_details(db, conversation_id)
    
    if not conversation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversation non trouvée",
        )
    
    # Vérifier que l'utilisateur est participant
    if current_user.id not in [conversation["mentor_id"], conversation["mentee_id"]]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Vous n'êtes pas autorisé à envoyer des messages dans cette conversation",
        )
    
    # Vérifier que le match est accepté
    if conversation["match_status"] != "accepted":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Vous ne pouvez pas envoyer de messages avant que le match soit accepté",
        )
    
    # Insérer le message
    insert_query = text("""
        INSERT INTO messages (conversation_id, sender_id, content)
        VALUES (:conversation_id, :sender_id, :content)
        RETURNING id, conversation_id, sender_id, content, is_read, created_at
    """)
    result = db.execute(insert_query, {
        "conversation_id": conversation_id,
        "sender_id": current_user.id,
        "content": message.content,
    })
    # Lire le résultat AVANT le commit : psycopg2 ferme le curseur après commit
    row = result.fetchone()
    msg_id = row.id
    msg_conv_id = row.conversation_id
    msg_sender_id = row.sender_id
    msg_content = row.content
    msg_is_read = row.is_read
    msg_created_at = row.created_at
    db.commit()
    
    # Mettre à jour updated_at de la conversation
    update_conv = text("""
        UPDATE conversations SET updated_at = NOW() WHERE id = :conversation_id
    """)
    db.execute(update_conv, {"conversation_id": conversation_id})
    db.commit()

    # Notifier l'autre participant en temps réel (SSE)
    other_user_id = (
        conversation["mentee_id"]
        if conversation["mentor_id"] == current_user.id
        else conversation["mentor_id"]
    )
    try:
        from routers.notifications import notify_user
        asyncio.create_task(notify_user(other_user_id, {
            "type": "new_message",
            "conversation_id": msg_conv_id,
            "message_id": msg_id,
            "sender_id": msg_sender_id,
            "sender_name": f"{current_user.first_name} {current_user.last_name}",
            "sender_photo": current_user.profile_photo,
            "content": msg_content,
            "created_at": msg_created_at.isoformat() if hasattr(msg_created_at, 'isoformat') else str(msg_created_at),
        }))
    except Exception as e:
        pass  # Ne pas bloquer l'envoi si la notification échoue

    return MessageResponse(
        id=msg_id,
        conversation_id=msg_conv_id,
        sender_id=msg_sender_id,
        sender=UserBasicResponse(
            id=current_user.id,
            first_name=current_user.first_name,
            last_name=current_user.last_name,
            profile_photo=current_user.profile_photo,
        ),
        content=msg_content,
        is_read=msg_is_read,
        created_at=msg_created_at,
    )


@router.post(
    "/conversations/direct",
    response_model=MessageResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Envoyer un message direct",
)
async def send_direct_message(
    request: DirectMessageRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> MessageResponse:
    """
    Envoie un message direct en créant un match et une conversation si nécessaire.
    """
    # 1. Vérifier si un match existe déjà
    match_query = text("""
        SELECT id, status FROM matches 
        WHERE (mentor_id = :u1 AND mentee_id = :u2)
           OR (mentor_id = :u2 AND mentee_id = :u1)
        LIMIT 1
    """)
    match_row = db.execute(match_query, {"u1": current_user.id, "u2": request.target_user_id}).fetchone()
    
    if match_row:
        match_id = match_row.id
        if match_row.status != "accepted":
            db.execute(text("UPDATE matches SET status = 'accepted' WHERE id = :match_id"), {"match_id": match_id})
    else:
        # Créer le match
        insert_match = text("""
            INSERT INTO matches (mentor_id, mentee_id, skill_id, score, status)
            VALUES (:mentor_id, :mentee_id, :skill_id, 100, 'accepted')
            RETURNING id
        """)
        result = db.execute(insert_match, {
            "mentor_id": request.target_user_id,
            "mentee_id": current_user.id,
            "skill_id": request.skill_id
        })
        match_id = result.scalar_one()
    db.commit()

    # 2. Vérifier/Créer la conversation
    conv_query = text("SELECT id FROM conversations WHERE match_id = :match_id LIMIT 1")
    conv_row = db.execute(conv_query, {"match_id": match_id}).fetchone()
    
    if conv_row:
        conversation_id = conv_row.id
    else:
        insert_conv = text("INSERT INTO conversations (match_id) VALUES (:match_id) RETURNING id")
        conv_res = db.execute(insert_conv, {"match_id": match_id})
        conversation_id = conv_res.scalar_one()
    db.commit()

    # 3. Insérer le message
    insert_msg = text("""
        INSERT INTO messages (conversation_id, sender_id, content)
        VALUES (:conversation_id, :sender_id, :content)
        RETURNING id, conversation_id, sender_id, content, is_read, created_at
    """)
    row = db.execute(insert_msg, {
        "conversation_id": conversation_id,
        "sender_id": current_user.id,
        "content": request.content,
    }).fetchone()
    
    msg_id = row.id
    msg_conv_id = row.conversation_id
    msg_sender_id = row.sender_id
    msg_content = row.content
    msg_is_read = row.is_read
    msg_created_at = row.created_at
    db.commit()

    update_conv = text("UPDATE conversations SET updated_at = NOW() WHERE id = :conversation_id")
    db.execute(update_conv, {"conversation_id": conversation_id})
    db.commit()

    # Notifier le destinataire en temps réel (SSE) pour les messages directs
    try:
        from routers.notifications import notify_user
        asyncio.create_task(notify_user(request.target_user_id, {
            "type": "new_message",
            "conversation_id": msg_conv_id,
            "message_id": msg_id,
            "sender_id": msg_sender_id,
            "sender_name": f"{current_user.first_name} {current_user.last_name}",
            "sender_photo": current_user.profile_photo,
            "content": msg_content,
            "created_at": msg_created_at.isoformat() if hasattr(msg_created_at, 'isoformat') else str(msg_created_at),
        }))
    except Exception:
        pass  # Ne pas bloquer si la notification SSE échoue

    return MessageResponse(
        id=msg_id,
        conversation_id=msg_conv_id,
        sender_id=msg_sender_id,
        sender=UserBasicResponse(
            id=current_user.id,
            first_name=current_user.first_name,
            last_name=current_user.last_name,
            profile_photo=current_user.profile_photo,
        ),
        content=msg_content,
        is_read=msg_is_read,
        created_at=msg_created_at,
    )


@router.put(
    "/messages/{message_id}/read",
    status_code=status.HTTP_200_OK,
    summary="Marquer un message comme lu",
)
async def mark_message_as_read(
    message_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Dict[str, str]:
    """
    Marque un message comme lu.
    """
    # Vérifier que le message existe
    check_query = text("""
        SELECT id, conversation_id, sender_id FROM messages WHERE id = :message_id
    """)
    existing = db.execute(check_query, {"message_id": message_id}).fetchone()
    
    if not existing:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Message non trouvé",
        )
    
    # Vérifier que l'utilisateur n'est pas l'expéditeur
    if existing.sender_id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Vous ne pouvez pas marquer vos propres messages comme lus",
        )
    
    # Marquer comme lu
    update_query = text("""
        UPDATE messages SET is_read = TRUE WHERE id = :message_id
    """)
    db.execute(update_query, {"message_id": message_id})
    db.commit()
    
    return {"message": "Message marqué comme lu"}