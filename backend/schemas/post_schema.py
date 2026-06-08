"""
Schémas Pydantic pour les posts de mentorat.
"""
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


class PostAvailabilityResponse(BaseModel):
    """Schéma pour les disponibilités d'un post."""
    id: int
    day_of_week: str
    start_time: str
    end_time: str

    class Config:
        from_attributes = True


class SkillBasicResponse(BaseModel):
    """Schéma minimal pour une compétence."""
    id: int
    name: str

    class Config:
        from_attributes = True


class UserBasicResponse(BaseModel):
    """Schéma minimal pour l'utilisateur."""
    id: int
    first_name: str
    last_name: str
    profile_photo: Optional[str] = None
    field_of_study: str
    level: str

    class Config:
        from_attributes = True


class PostResponse(BaseModel):
    """Schéma pour la réponse d'un post."""
    id: int
    user_id: int
    user: UserBasicResponse
    type: str  # 'offer' ou 'request'
    skill_id: int
    skill: SkillBasicResponse
    mode: str  # 'online', 'offline', 'both'
    description: Optional[str] = None
    is_active: bool
    created_at: datetime
    updated_at: datetime
    availabilities: List[PostAvailabilityResponse] = []

    class Config:
        from_attributes = True


class CreatePostRequest(BaseModel):
    """Schéma pour créer un nouveau post."""
    type: str = Field(..., pattern="^(offer|request)$")
    skill_id: int
    mode: str = Field(..., pattern="^(online|offline|both)$")
    description: Optional[str] = None
    availabilities: Optional[List[dict]] = None
    # Structure des availabilities:
    # [{"day_of_week": "Monday", "start_time": "14:00", "end_time": "17:00"}]


class UpdatePostRequest(BaseModel):
    """Schéma pour mettre à jour un post."""
    skill_id: Optional[int] = None
    mode: Optional[str] = Field(None, pattern="^(online|offline|both)$")
    description: Optional[str] = None
    is_active: Optional[bool] = None
    availabilities: Optional[List[dict]] = None


class PostListResponse(BaseModel):
    """Schéma pour la liste des posts."""
    posts: List[PostResponse]
    total: int