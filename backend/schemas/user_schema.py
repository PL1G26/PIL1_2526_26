"""
Schémas Pydantic pour les utilisateurs.
"""
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


class SkillResponse(BaseModel):
    """Schéma pour une compétence."""
    id: int
    name: str

    class Config:
        from_attributes = True


class UserSkillResponse(BaseModel):
    """Schéma pour une compétence d'utilisateur."""
    skill_id: int
    skill: SkillResponse
    proficiency: str  # 'strong' ou 'weak'

    class Config:
        from_attributes = True


class AvailabilityResponse(BaseModel):
    """Schéma pour une disponibilité."""
    id: int
    day_of_week: str
    start_time: str
    end_time: str

    class Config:
        from_attributes = True


class UserProfileResponse(BaseModel):
    """Schéma pour le profil utilisateur (réponse)."""
    id: int
    first_name: str
    last_name: str
    email: str
    phone_number: str
    profile_photo: Optional[str] = None
    field_of_study: str
    level: str
    bio: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    skills: List[UserSkillResponse] = []
    availabilities: List[AvailabilityResponse] = []

    class Config:
        from_attributes = True


class UpdateProfileRequest(BaseModel):
    """Schéma pour la mise à jour du profil."""
    first_name: Optional[str] = Field(None, min_length=1, max_length=50)
    last_name: Optional[str] = Field(None, min_length=1, max_length=50)
    profile_photo: Optional[str] = None
    field_of_study: Optional[str] = Field(None, pattern="^(IA|IM|GL|SE&IoT|SI)$")
    level: Optional[str] = Field(None, pattern="^(L1|L2|L3|M1|M2)$")
    bio: Optional[str] = None


class AddSkillRequest(BaseModel):
    """Schéma pour ajouter une compétence."""
    skill_id: int
    proficiency: str = Field(..., pattern="^(strong|weak)$")


class AddAvailabilityRequest(BaseModel):
    """Schéma pour ajouter une disponibilité."""
    day_of_week: str = Field(..., pattern="^(Monday|Tuesday|Wednesday|Thursday|Friday|Saturday|Sunday)$")
    start_time: str  # Format: "HH:MM"
    end_time: str    # Format: "HH:MM"


class UserBasicResponse(BaseModel):
    """Schéma minimal pour les infos de base d'un utilisateur."""
    id: int
    first_name: str
    last_name: str
    profile_photo: Optional[str] = None
    field_of_study: str
    level: str

    class Config:
        from_attributes = True