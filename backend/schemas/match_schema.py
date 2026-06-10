"""
Schémas Pydantic pour les correspondances (matches).
"""
from pydantic import BaseModel, ConfigDict
from typing import Optional
from datetime import datetime


class SkillBasicResponse(BaseModel):
    """Schéma minimal pour une compétence."""
    id: int
    name: str

    model_config = ConfigDict(from_attributes=True)


class UserBasicResponse(BaseModel):
    """Schéma minimal pour un utilisateur."""
    id: int
    first_name: str
    last_name: str
    profile_photo: Optional[str] = None
    field_of_study: str
    level: str

    model_config = ConfigDict(from_attributes=True)


class MatchResponse(BaseModel):
    """Schéma pour une correspondance mentor-mentoré."""
    id: int
    mentor_id: int
    mentee_id: int
    mentor: UserBasicResponse
    mentee: UserBasicResponse
    offer_post_id: Optional[int] = None
    request_post_id: Optional[int] = None
    skill_id: int
    skill: SkillBasicResponse
    score: float  # Score sur 100
    status: str  # 'pending', 'accepted', 'rejected'
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class MatchListResponse(BaseModel):
    """Schéma pour la liste des matches."""
    matches: list[MatchResponse]
    total: int


class AcceptMatchResponse(BaseModel):
    """Schéma de réponse après acceptation d'un match."""
    message: str
    match_id: int
    conversation_id: int


class RejectMatchResponse(BaseModel):
    """Schéma de réponse après refus d'un match."""
    message: str
    match_id: int