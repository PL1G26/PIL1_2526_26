# ============================================================
# IFRI_MentorLink — Test Script pour les Services
# backend/test_services.py
# ============================================================

import sys
import os
# Ajoute backend/ au sys.path → permet d'importer database, models, services, etc.
# Fonctionne que le script soit lancé avec pytest OU python3 directement.
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from typing import Dict, List, Optional
from datetime import datetime

from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError

from database import SessionLocal
from models import User, Skill, Match
from services.auth_service import (
    hash_password,
    verify_password,
    create_access_token,
    decode_access_token,
)
from services.matching_service import (
    calculate_score,
    compute_matches_for_user,
    create_match_record,
)
from services.chat_service import (
    get_conversation_by_match,
    create_conversation_for_match,
    can_user_access_conversation,
    create_message,
    mark_message_as_read,
    ensure_conversation_for_match,
)

TEST_SKILL_NAME = "unittest_service_skill_2026"
TEST_USER_EMAIL_PREFIX = "unittest_service_user"


def _execute_sql(db, query: str, params: Dict = None):
    return db.execute(text(query), params or {})


def _create_test_skill(db) -> tuple[int, bool]:
    existing = db.query(Skill).filter(Skill.name == TEST_SKILL_NAME).first()
    if existing:
        return existing.id, False

    skill = Skill(name=TEST_SKILL_NAME)
    db.add(skill)
    db.commit()
    db.refresh(skill)
    return skill.id, True


def _delete_test_skill(db, skill_id: int):
    db.query(Skill).filter(Skill.id == skill_id, Skill.name == TEST_SKILL_NAME).delete()
    db.commit()


def _create_test_user(db, display_name: str, field_of_study: str, level: str) -> tuple[int, bool]:
    email = f"{TEST_USER_EMAIL_PREFIX}_{display_name.lower()}@test.com"
    phone = f"+2299000{hash(display_name) % 10000:04d}"
    user = db.query(User).filter(User.email == email).first()
    if user:
        return user.id, False

    user = User(
        first_name=display_name,
        last_name="ServiceTest",
        email=email,
        phone_number=phone,
        password_hash=hash_password("Test1234!"),
        field_of_study=field_of_study,
        level=level,
        bio="Utilisateur de test pour services",
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user.id, True


def _delete_test_user(db, user_id: int):
    db.query(User).filter(User.id == user_id).delete()
    db.commit()


def _insert_user_skill(db, user_id: int, skill_id: int, proficiency: str):
    _execute_sql(
        db,
        "INSERT INTO user_skills (user_id, skill_id, proficiency) VALUES (:user_id, :skill_id, :proficiency)",
        {"user_id": user_id, "skill_id": skill_id, "proficiency": proficiency},
    )
    db.commit()


def _insert_user_availability(db, user_id: int, day_of_week: str, start_time: str, end_time: str):
    _execute_sql(
        db,
        "INSERT INTO user_availabilities (user_id, day_of_week, start_time, end_time) VALUES (:user_id, :day_of_week, :start_time, :end_time)",
        {
            "user_id": user_id,
            "day_of_week": day_of_week,
            "start_time": start_time,
            "end_time": end_time,
        },
    )
    db.commit()


def _delete_user_skills(db, user_id: int):
    _execute_sql(db, "DELETE FROM user_skills WHERE user_id = :user_id", {"user_id": user_id})
    db.commit()


def _delete_user_availabilities(db, user_id: int):
    _execute_sql(db, "DELETE FROM user_availabilities WHERE user_id = :user_id", {"user_id": user_id})
    db.commit()


def _delete_test_match(db, match_id: int):
    db.query(Match).filter(Match.id == match_id).delete()
    db.commit()


def test_auth_service():
    print("\n🔐 Test auth_service...")

    password = "SuperSecret123!"
    hashed = hash_password(password)
    if not verify_password(password, hashed):
        print("  ✗ hash_password / verify_password a échoué")
        return False

    if verify_password("wrong-password", hashed):
        print("  ✗ verify_password accepte un mot de passe incorrect")
        return False

    print("  ✓ hash_password / verify_password fonctionne")

    token = create_access_token({"sub": "42"})
    payload = decode_access_token(token)
    if payload.get("sub") != "42":
        print("  ✗ create_access_token / decode_access_token a renvoyé un payload incorrect")
        return False

    print("  ✓ create_access_token / decode_access_token fonctionne")
    return True


def test_matching_service_score():
    print("\n🎯 Test matching_service.calculate_score...")

    mentor = {
        "field_of_study": "IA",
        "skills": [{"skill_id": 1, "proficiency": "strong"}],
        "availabilities": [
            {"day_of_week": "Monday", "start_time": "10:00", "end_time": "12:00"}
        ],
    }
    mentee = {
        "field_of_study": "IA",
        "skills": [{"skill_id": 1, "proficiency": "weak"}],
        "availabilities": [
            {"day_of_week": "Monday", "start_time": "11:00", "end_time": "13:00"}
        ],
    }
    score = calculate_score(mentor=mentor, mentee=mentee, skill_id=1)
    expected = 100.0
    if score != expected:
        print(f"  ✗ score attendu={expected}, obtenu={score}")
        return False

    print("  ✓ calculate_score retourne 100 pour une correspondance parfaite")

    mentee["field_of_study"] = "IM"
    score = calculate_score(mentor=mentor, mentee=mentee, skill_id=1)
    if score != 85.0:
        print(f"  ✗ score attendu=85.0 pour filières proches, obtenu={score}")
        return False

    print("  ✓ calculate_score gère les filières liées correctement")
    return True


def test_matching_service_integration():
    print("\n🔗 Test matching_service.compute_matches_for_user (intégration DB)...")
    db = SessionLocal()
    created = {
        "skill_id": None,
        "skill_created": False,
        "mentor_id": None,
        "mentor_created": False,
        "mentee_id": None,
        "mentee_created": False,
        "match_id": None,
        "conversation_id": None,
        "message_id": None,
    }

    try:
        created["skill_id"], created["skill_created"] = _create_test_skill(db)
        created["mentor_id"], created["mentor_created"] = _create_test_user(db, "MentorA", "IA", "L2")
        created["mentee_id"], created["mentee_created"] = _create_test_user(db, "MenteeA", "IM", "L1")

        _insert_user_skill(db, created["mentor_id"], created["skill_id"], "strong")
        _insert_user_skill(db, created["mentee_id"], created["skill_id"], "weak")
        _insert_user_availability(db, created["mentor_id"], "Monday", "10:00", "12:00")
        _insert_user_availability(db, created["mentee_id"], "Monday", "11:00", "13:00")

        matches = compute_matches_for_user(db, created["mentee_id"])
        if len(matches) == 0:
            print("  ✗ Aucun match trouvé alors qu'une correspondance existe")
            return False

        match = matches[0]
        if match["mentor_id"] != created["mentor_id"] or match["mentee_id"] != created["mentee_id"]:
            print("  ✗ Le match retourné n'associe pas les bons utilisateurs")
            return False

        if match["score"] < 40.0:
            print("  ✗ Le score du match est inférieur au seuil attendu")
            return False

        print("  ✓ compute_matches_for_user retourne un match valide")
        return True
    except SQLAlchemyError as exc:
        print(f"  ✗ Erreur DB pendant le test matching: {exc}")
        db.rollback()
        return False
    finally:
        try:
            if created["mentee_id"]:
                _delete_user_skills(db, created["mentee_id"])
                _delete_user_availabilities(db, created["mentee_id"])
                if created["mentee_created"]:
                    _delete_test_user(db, created["mentee_id"])
            if created["mentor_id"]:
                _delete_user_skills(db, created["mentor_id"])
                _delete_user_availabilities(db, created["mentor_id"])
                if created["mentor_created"]:
                    _delete_test_user(db, created["mentor_id"])
            if created["skill_id"] and created["skill_created"]:
                _delete_test_skill(db, created["skill_id"])
        except Exception:
            pass
        db.close()


def test_chat_service_integration():
    print("\n💬 Test chat_service (intégration DB)...")
    db = SessionLocal()
    created = {
        "mentor_id": None,
        "mentor_created": False,
        "mentee_id": None,
        "mentee_created": False,
        "match_id": None,
        "conversation_id": None,
        "message_id": None,
    }

    try:
        created["mentee_id"], created["mentee_created"] = _create_test_user(db, "ChatMentee", "IM", "L1")
        created["mentor_id"], created["mentor_created"] = _create_test_user(db, "ChatMentor", "IA", "L2")

        match = create_match_record(
            db,
            mentor_id=created["mentor_id"],
            mentee_id=created["mentee_id"],
            score=80.0,
            status="accepted",
        )
        created["match_id"] = match.id

        conversation = ensure_conversation_for_match(db, created["match_id"])
        created["conversation_id"] = conversation.id

        if not can_user_access_conversation(db, conversation.id, created["mentor_id"]):
            print("  ✗ Mentor ne peut pas accéder à la conversation acceptée")
            return False

        if not can_user_access_conversation(db, conversation.id, created["mentee_id"]):
            print("  ✗ Mentee ne peut pas accéder à la conversation acceptée")
            return False

        message = create_message(db, conversation.id, created["mentor_id"], "Bonjour, test de message")
        created["message_id"] = message.id
        if message.content != "Bonjour, test de message":
            print("  ✗ Le contenu du message n'est pas correctement enregistré")
            return False

        saved = mark_message_as_read(db, message.id)
        if not saved or not saved.is_read:
            print("  ✗ mark_message_as_read n'a pas mis le message en lecture")
            return False

        print("  ✓ chat_service fonctionne pour création et accès aux messages")
        return True
    except SQLAlchemyError as exc:
        print(f"  ✗ Erreur DB pendant le test chat: {exc}")
        db.rollback()
        return False
    finally:
        try:
            if created["message_id"]:
                _execute_sql(db, "DELETE FROM messages WHERE id = :id", {"id": created["message_id"]})
            if created["conversation_id"]:
                _execute_sql(db, "DELETE FROM conversations WHERE id = :id", {"id": created["conversation_id"]})
            if created["match_id"]:
                _delete_test_match(db, created["match_id"])
            if created["mentor_id"] and created["mentor_created"]:
                _delete_test_user(db, created["mentor_id"])
            if created["mentee_id"] and created["mentee_created"]:
                _delete_test_user(db, created["mentee_id"])
            db.commit()
        except Exception:
            pass
        db.close()


def run_all_tests():
    print("=" * 60)
    print("🧪 TESTS DES SERVICES - IFRI_MentorLink")
    print("=" * 60)

    tests = [
        (test_auth_service, "auth_service"),
        (test_matching_service_score, "matching_service (unit)")
    ]

    all_ok = True
    for fn, name in tests:
        ok = fn()
        print(f"{name}: {'PASS' if ok else 'FAIL'}")
        if not ok:
            all_ok = False

    # Tests d'intégration DB
    integration_tests = [
        (test_matching_service_integration, "matching_service (DB)"),
        (test_chat_service_integration, "chat_service (DB)"),
    ]
    for fn, name in integration_tests:
        ok = fn()
        print(f"{name}: {'PASS' if ok else 'FAIL'}")
        if not ok:
            all_ok = False

    print("\n" + "=" * 60)
    if all_ok:
        print("✅ TOUS LES TESTS DES SERVICES ONT RÉUSSI")
    else:
        print("⚠️ CERTAINS TESTS ONT ÉCHOUÉ. Vérifiez les messages ci-dessus.")


if __name__ == "__main__":
    run_all_tests()
