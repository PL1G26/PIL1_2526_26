"""Service de calcul des correspondances mentor / mentoré."""

from datetime import datetime, timezone
from typing import Any, Dict, List

from sqlalchemy import text
from sqlalchemy.orm import Session

from models.user import User
from models import Match

RELATED_FIELDS = {
    "IA": ["IM", "GL"],
    "IM": ["IA", "GL"],
    "GL": ["IA", "IM", "SI"],
    "SI": ["GL"],
    "SE&IoT": ["IA"],
}


def _load_user_skills(db: Session, user_id: int) -> List[Dict[str, Any]]:
    query = text(
        "SELECT user_id, skill_id, proficiency FROM user_skills WHERE user_id = :user_id"
    )
    return [dict(row) for row in db.execute(query, {"user_id": user_id}).mappings().all()]


def _load_user_availabilities(db: Session, user_id: int) -> List[Dict[str, Any]]:
    query = text(
        "SELECT day_of_week, start_time, end_time FROM user_availabilities WHERE user_id = :user_id"
    )
    return [dict(row) for row in db.execute(query, {"user_id": user_id}).mappings().all()]


def _count_common_slots(
    mentor_slots: List[Dict[str, Any]], mentee_slots: List[Dict[str, Any]]
) -> int:
    common = 0
    for mentor_slot in mentor_slots:
        for mentee_slot in mentee_slots:
            if mentor_slot["day_of_week"] != mentee_slot["day_of_week"]:
                continue

            if (
                mentor_slot["start_time"] < mentee_slot["end_time"]
                and mentee_slot["start_time"] < mentor_slot["end_time"]
            ):
                common += 1
    return common


def calculate_score(
    mentor: Dict[str, Any], mentee: Dict[str, Any], skill_id: int
) -> float:
    """Calcule le score de compatibilité entre un mentor et un mentoré pour une compétence."""
    score = 0.0

    mentor_strong = {
        item["skill_id"]
        for item in mentor.get("skills", [])
        if item.get("proficiency") == "strong"
    }
    mentee_weak = {
        item["skill_id"]
        for item in mentee.get("skills", [])
        if item.get("proficiency") == "weak"
    }

    if skill_id in mentor_strong and skill_id in mentee_weak:
        score += 40.0

    common_slots = _count_common_slots(
        mentor.get("availabilities", []), mentee.get("availabilities", [])
    )
    score += min(30.0, common_slots * 30.0)

    mentor_field = mentor.get("field_of_study", "")
    mentee_field = mentee.get("field_of_study", "")
    if mentor_field == mentee_field:
        score += 30.0
    elif mentee_field in RELATED_FIELDS.get(mentor_field, []):
        score += 15.0

    return round(score, 2)


def compute_matches_for_user(db: Session, current_user_id: int) -> List[Dict[str, Any]]:
    """Calcule les matches possibles pour un utilisateur donné."""
    user = db.query(User).filter(User.id == current_user_id).first()
    if user is None:
        return []

    all_users = db.query(User).all()
    user_ids = [u.id for u in all_users]

    skills_query = text(
        "SELECT user_id, skill_id, proficiency FROM user_skills WHERE user_id = ANY(:user_ids)"
    )
    all_skills = db.execute(skills_query, {"user_ids": user_ids}).mappings().all()
    user_skills_map = {uid: [] for uid in user_ids}
    for row in all_skills:
        user_skills_map[row["user_id"]].append(dict(row))

    avails_query = text(
        "SELECT user_id, day_of_week, start_time, end_time FROM user_availabilities WHERE user_id = ANY(:user_ids)"
    )
    all_avails = db.execute(avails_query, {"user_ids": user_ids}).mappings().all()
    user_avails_map = {uid: [] for uid in user_ids}
    for row in all_avails:
        user_avails_map[row["user_id"]].append(dict(row))

    user_data = {
        "id": user.id,
        "field_of_study": user.field_of_study,
        "level": user.level,
        "skills": user_skills_map.get(user.id, []),
        "availabilities": user_avails_map.get(user.id, []),
    }

    matches: List[Dict[str, Any]] = []

    user_weak_skills = {
        item["skill_id"]
        for item in user_data["skills"]
        if item["proficiency"] == "weak"
    }

    for other in all_users:
        if other.id == current_user_id:
            continue

        other_data = {
            "id": other.id,
            "field_of_study": other.field_of_study,
            "level": other.level,
            "skills": user_skills_map.get(other.id, []),
            "availabilities": user_avails_map.get(other.id, []),
        }

        other_strong_skills = {
            item["skill_id"]
            for item in other_data["skills"]
            if item["proficiency"] == "strong"
        }

        available_skills = user_weak_skills & other_strong_skills
        for skill_id in available_skills:
            score = calculate_score(mentor=other_data, mentee=user_data, skill_id=skill_id)
            if score >= 40.0:
                matches.append(
                    {
                        "mentor_id": other.id,
                        "mentee_id": user.id,
                        "skill_id": skill_id,
                        "score": score,
                        "status": "pending",
                        "created_at": datetime.now(timezone.utc),
                    }
                )

    matches.sort(key=lambda item: item["score"], reverse=True)
    return matches


def create_match_record(
    db: Session,
    mentor_id: int,
    mentee_id: int,
    score: float = 0.0,
    status: str = "pending",
    skill_id: int | None = None,
    offer_post_id: int | None = None,
    request_post_id: int | None = None,
) -> Match:
    """Create a Match record while normalizing the order so that
    `mentor_id > mentee_id` to satisfy DB constraints.

    Returns the created Match instance.
    """
    # Ensure ordering to satisfy CHECK (mentor_id > mentee_id)
    if mentor_id <= mentee_id:
        mentor_id, mentee_id = mentee_id, mentor_id

    match = Match(
        mentor_id=mentor_id,
        mentee_id=mentee_id,
        score=score,
        status=status,
        skill_id=skill_id,
        offer_post_id=offer_post_id,
        request_post_id=request_post_id,
    )
    db.add(match)
    db.commit()
    db.refresh(match)
    return match
