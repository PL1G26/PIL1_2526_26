# ============================================================
# IFRI_MentorLink — Notifications Router (SSE)
# backend/routers/notifications.py
# Fournit un flux Server-Sent Events pour les nouvelles notifications
# de messages en temps réel.
# ============================================================

import asyncio
import json
import logging
from datetime import datetime, timezone
from typing import AsyncGenerator, Dict, Optional, Set

from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from fastapi.responses import StreamingResponse
from jose import JWTError
from sqlalchemy.orm import Session
from sqlalchemy import text

from config import settings
from database import get_db
from models.user import User
from services.auth_service import decode_access_token
from routers.auth import get_current_user

logger = logging.getLogger(__name__)

router = APIRouter()


# ──── DÉPENDANCE SSE DÉDIÉE ───────────────────────────────────
# L'EventSource navigateur ne supporte pas les headers personnalisés.
# On accepte donc le token JWT en query param pour ce seul endpoint.
async def _get_sse_user(
    token: Optional[str] = Query(default=None, alias="token"),
    db: Session = Depends(get_db),
) -> User:
    """Valide un token JWT passé en query param (pour EventSource)."""
    if not token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token manquant")
    try:
        payload = decode_access_token(token)
        user_id: str = payload.get("sub")
        if not user_id:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token invalide")
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token invalide")
    user = db.query(User).filter(User.id == int(user_id)).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Utilisateur introuvable")
    return user


# ──── REGISTRE DES CONNEXIONS ACTIVES ────────────────────────
# Dictionnaire : user_id → set of asyncio.Queue
_connections: Dict[int, Set[asyncio.Queue]] = {}


def _get_or_create_queues(user_id: int) -> Set[asyncio.Queue]:
    if user_id not in _connections:
        _connections[user_id] = set()
    return _connections[user_id]


async def _notify_user(user_id: int, event_data: dict) -> None:
    """Envoie un événement SSE à toutes les connexions d'un utilisateur."""
    queues = _connections.get(user_id, set())
    dead = set()
    for q in queues:
        try:
            await q.put(event_data)
        except Exception:
            dead.add(q)
    for q in dead:
        queues.discard(q)


# Expose pour être appelé depuis d'autres routers
notify_user = _notify_user


async def _event_generator(
    request: Request,
    user_id: int,
    queue: asyncio.Queue,
) -> AsyncGenerator[str, None]:
    """Générateur asynchrone d'événements SSE."""
    # Enregistrer la connexion
    queues = _get_or_create_queues(user_id)
    queues.add(queue)

    try:
        # Premier événement : connexion établie
        yield f"data: {json.dumps({'type': 'connected', 'userId': user_id})}\n\n"

        while True:
            # Vérifier que le client est encore connecté
            if await request.is_disconnected():
                break

            try:
                # Attendre un événement pendant 25 secondes max, puis envoyer un ping
                event = await asyncio.wait_for(queue.get(), timeout=25.0)
                yield f"data: {json.dumps(event)}\n\n"
            except asyncio.TimeoutError:
                # Ping heartbeat pour maintenir la connexion ouverte
                yield f"data: {json.dumps({'type': 'ping', 'ts': datetime.now(timezone.utc).isoformat()})}\n\n"

    except asyncio.CancelledError:
        pass
    finally:
        queues.discard(queue)
        if not queues:
            _connections.pop(user_id, None)
        logger.debug(f"SSE connexion fermée pour user {user_id}")


# ──── ENDPOINT SSE ────────────────────────────────────────────
@router.get(
    "/notifications/stream",
    summary="Flux SSE de notifications en temps réel",
)
async def notification_stream(
    request: Request,
    current_user: User = Depends(_get_sse_user),
) -> StreamingResponse:
    """
    Ouvre un flux Server-Sent Events.
    Le client reçoit un événement JSON à chaque nouveau message
    adressé à l'utilisateur connecté.
    """
    queue: asyncio.Queue = asyncio.Queue()

    return StreamingResponse(
        _event_generator(request, current_user.id, queue),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
            "Connection": "keep-alive",
        },
    )


# ──── ENDPOINT UNREAD COUNT ───────────────────────────────────
@router.get(
    "/notifications/unread-count",
    summary="Nombre de messages non lus (polling fallback)",
)
async def get_unread_count(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> dict:
    """
    Retourne le total des messages non lus et un résumé
    par conversation pour l'utilisateur connecté.
    """
    query = text("""
        SELECT
            c.id as conversation_id,
            COUNT(m.id) as unread_count,
            u.first_name as sender_first_name,
            u.last_name as sender_last_name,
            MAX(m.content) as last_content
        FROM messages m
        JOIN conversations c ON m.conversation_id = c.id
        JOIN matches mt ON c.match_id = mt.id
        JOIN users u ON m.sender_id = u.id
        WHERE m.sender_id != :user_id
          AND m.is_read = FALSE
          AND (mt.mentor_id = :user_id OR mt.mentee_id = :user_id)
        GROUP BY c.id, u.first_name, u.last_name
    """)
    rows = db.execute(query, {"user_id": current_user.id}).fetchall()

    conversations = [
        {
            "conversation_id": row.conversation_id,
            "unread_count": row.unread_count,
            "sender_name": f"{row.sender_first_name} {row.sender_last_name}",
            "last_content": row.last_content,
        }
        for row in rows
    ]
    total = sum(r["unread_count"] for r in conversations)

    return {"total_unread": total, "conversations": conversations}


# ──── ENDPOINT MARK CONVERSATION AS READ ─────────────────────
@router.put(
    "/conversations/{conversation_id}/read",
    summary="Marquer tous les messages d'une conversation comme lus",
)
async def mark_conversation_read(
    conversation_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> dict:
    """
    Marque tous les messages non lus d'une conversation comme lus
    pour l'utilisateur courant (messages dont il n'est pas l'expéditeur).
    """
    update_query = text("""
        UPDATE messages
        SET is_read = TRUE
        WHERE conversation_id = :conversation_id
          AND sender_id != :user_id
          AND is_read = FALSE
    """)
    result = db.execute(
        update_query,
        {"conversation_id": conversation_id, "user_id": current_user.id},
    )
    db.commit()
    marked = result.rowcount

    return {"message": f"{marked} message(s) marqué(s) comme lu(s)", "marked": marked}
