# ============================================================
# IFRI_MentorLink — Chat Router
# backend/routers/chat.py
# Endpoints: conversations, messages
# ============================================================

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
    # Récupérer toutes les conversations où l'utilisateur est participant
    query = text("""
        SELECT 
            c.id, c.match_id, c.created_at, c.updated_at,
            m.mentor_id, m.mentee_id, m.status as match_status
        FROM conversations c
        JOIN matches m ON c.match_id = m.id
        WHERE m.status = 'accepted'
        AND (m.mentor_id = :user_id OR m.mentee_id = :user_id)
        ORDER BY c.updated_at DESC
    """)
    result = db.execute(query, {"user_id": current_user.id}).fetchall()
    
    conversations = []
    for row in result:
        # Récupérer l'autre utilisateur
        other_user_id = row.mentee_id if row.mentor_id == current_user.id else row.mentor_id
        user_query = text("""
            SELECT id, first_name, last_name, profile_photo
            FROM users WHERE id = :user_id
        """)
        user_result = db.execute(user_query, {"user_id": other_user_id}).fetchone()
        
        other_user = {
            "id": user_result.id,
            "first_name": user_result.first_name,
            "last_name": user_result.last_name,
            "profile_photo": user_result.profile_photo,
        }
        
        # Récupérer le dernier message
        last_msg_query = text("""
            SELECT id, conversation_id, sender_id, content, is_read, created_at
            FROM messages
            WHERE conversation_id = :conv_id
            ORDER BY created_at DESC
            LIMIT 1
        """)
        last_msg = db.execute(last_msg_query, {"conv_id": row.id}).fetchone()
        
        # Récupérer le sender du dernier message
        sender = None
        if last_msg:
            sender_query = text("""
                SELECT id, first_name, last_name, profile_photo
                FROM users WHERE id = :sender_id
            """)
            sender_result = db.execute(sender_query, {"sender_id": last_msg.sender_id}).fetchone()
            sender = {
                "id": sender_result.id,
                "first_name": sender_result.first_name,
                "last_name": sender_result.last_name,
                "profile_photo": sender_result.profile_photo,
            }
        
        # Compter les messages non lus
        unread_query = text("""
            SELECT COUNT(*) as count
            FROM messages
            WHERE conversation_id = :conv_id
            AND sender_id != :user_id
            AND is_read = FALSE
        """)
        unread_result = db.execute(unread_query, {"conv_id": row.id, "user_id": current_user.id}).fetchone()
        
        last_message = None
        if last_msg and sender:
            last_message = MessageResponse(
                id=last_msg.id,
                conversation_id=last_msg.conversation_id,
                sender_id=last_msg.sender_id,
                sender=UserBasicResponse(**sender),
                content=last_msg.content,
                is_read=last_msg.is_read,
                created_at=last_msg.created_at,
            )
        
        conversations.append(
            ConversationResponse(
                id=row.id,
                match_id=row.match_id,
                other_user=UserBasicResponse(**other_user),
                last_message=last_message,
                unread_count=unread_result.count if unread_result else 0,
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
    db.commit()
    
    # Mettre à jour updated_at de la conversation
    update_conv = text("""
        UPDATE conversations SET updated_at = NOW() WHERE id = :conversation_id
    """)
    db.execute(update_conv, {"conversation_id": conversation_id})
    db.commit()
    
    return MessageResponse(
        id=row.id,
        conversation_id=row.conversation_id,
        sender_id=row.sender_id,
        sender=UserBasicResponse(
            id=current_user.id,
            first_name=current_user.first_name,
            last_name=current_user.last_name,
            profile_photo=current_user.profile_photo,
        ),
        content=row.content,
        is_read=row.is_read,
        created_at=row.created_at,
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