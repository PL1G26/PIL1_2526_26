"""Service de vérification et de création de conversations / messages."""

from typing import Optional

from sqlalchemy.orm import Session

from models.conversation import Conversation
from models.match import Match
from models.message import Message


def get_conversation_by_match(db: Session, match_id: int) -> Optional[Conversation]:
    """Retourne la conversation liée à un match si elle existe."""
    return db.query(Conversation).filter(Conversation.match_id == match_id).first()


def create_conversation_for_match(db: Session, match_id: int) -> Conversation:
    """Crée une conversation pour un match accepté."""
    conversation = Conversation(match_id=match_id)
    db.add(conversation)
    db.commit()
    db.refresh(conversation)
    return conversation


def can_user_access_conversation(db: Session, conversation_id: int, user_id: int) -> bool:
    """Vérifie si l'utilisateur appartient à la conversation via le match associé."""
    conversation = db.query(Conversation).filter(Conversation.id == conversation_id).first()
    if conversation is None:
        return False

    match = db.query(Match).filter(Match.id == conversation.match_id).first()
    if match is None or match.status != "accepted":
        return False

    return user_id in {match.mentor_id, match.mentee_id}


def can_user_send_message(db: Session, conversation_id: int, user_id: int) -> bool:
    """Vérifie si l'utilisateur peut envoyer un message dans la conversation."""
    return can_user_access_conversation(db, conversation_id, user_id)


def create_message(db: Session, conversation_id: int, sender_id: int, content: str) -> Message:
    """Crée et retourne un message dans une conversation valide."""
    message = Message(
        conversation_id=conversation_id,
        sender_id=sender_id,
        content=content,
        is_read=False,
    )
    db.add(message)
    db.commit()
    db.refresh(message)
    return message


def mark_message_as_read(db: Session, message_id: int) -> Optional[Message]:
    """Marque un message comme lu et retourne le message mis à jour."""
    message = db.query(Message).filter(Message.id == message_id).first()
    if message is None:
        return None
    message.is_read = True
    db.commit()
    db.refresh(message)
    return message


def ensure_conversation_for_match(db: Session, match_id: int) -> Conversation:
    """Récupère ou crée une conversation associée à un match accepté."""
    match = db.query(Match).filter(Match.id == match_id).first()
    if match is None:
        raise ValueError("Match introuvable")
    if match.status != "accepted":
        raise ValueError("La conversation ne peut être créée que pour un match accepté")

    conversation = get_conversation_by_match(db, match_id)
    if conversation is None:
        conversation = create_conversation_for_match(db, match_id)
    return conversation
