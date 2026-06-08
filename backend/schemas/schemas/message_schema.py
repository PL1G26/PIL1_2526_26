"""
Schémas Pydantic pour les messages.
"""
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class UserBasicResponse(BaseModel):
    """Schéma minimal pour un utilisateur."""
    id: int
    first_name: str
    last_name: str
    profile_photo: Optional[str] = None

    class Config:
        from_attributes = True


class MessageResponse(BaseModel):
    """Schéma pour un message."""
    id: int
    conversation_id: int
    sender_id: int
    sender: UserBasicResponse
    content: str
    is_read: bool
    created_at: datetime

    class Config:
        from_attributes = True


class SendMessageRequest(BaseModel):
    """Schéma pour envoyer un message."""
    content: str = Field(..., min_length=1)


class MessageListResponse(BaseModel):
    """Schéma pour la liste des messages."""
    messages: list[MessageResponse]
    total: int


class ConversationResponse(BaseModel):
    """Schéma pour une conversation."""
    id: int
    match_id: int
    other_user: UserBasicResponse  # L'autre participant (pas soi-même)
    last_message: Optional[MessageResponse] = None
    unread_count: int = 0
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ConversationListResponse(BaseModel):
    """Schéma pour la liste des conversations."""
    conversations: list[ConversationResponse]
    total: int


class MarkReadResponse(BaseModel):
    """Schéma de réponse après marquage comme lu."""
    message: str
    messages_marked_read: int